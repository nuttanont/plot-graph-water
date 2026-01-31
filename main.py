"""
Water Level Monitoring System
==============================
Connects to Thai water station websockets, generates water level graphs,
uploads to Cloudinary, and sends notifications to LINE Messaging API.

Usage:
    python main.py 703           # Monitor single station
    python main.py 703 704 705   # Monitor multiple stations
"""

# ============================================================================
# IMPORTS
# ============================================================================

# Standard library imports
import asyncio                    # For async websocket connections
import json                       # For parsing JSON data
import os                         # For environment variables and file paths
import sys                        # For command-line arguments
import uuid                       # For generating unique LINE retry keys
from datetime import datetime     # For timestamp conversion

# Third-party imports
import cloudinary                 # Cloudinary SDK for image hosting
import cloudinary.uploader
import matplotlib.dates as mdates # For formatting datetime on graph axes
import matplotlib.pyplot as plt   # For creating graphs
import requests                   # For HTTP requests to LINE API
import websockets                 # For websocket connections
from dotenv import load_dotenv    # For loading .env file

# ============================================================================
# CONFIGURATION
# ============================================================================

# Load environment variables from .env file
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, '.env')
load_dotenv(env_path)

# Configure Cloudinary for image hosting
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

# Configure matplotlib to support Thai characters
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for Docker
import matplotlib.font_manager as fm

# Rebuild font cache and find available fonts
fm._load_fontmanager(try_read_cache=False)

# Set font configuration - explicitly use Thai-capable fonts
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Laksaman', 'Sawasdee New', 'DejaVu Sans', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# Enable font fallback for missing glyphs (critical for Thai characters)
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

# ============================================================================
# DATA PROCESSING FUNCTIONS
# ============================================================================

def load_water_level_graph(payload: dict) -> tuple[list[datetime], list[float]]:
    """
    Extract water level graph data from websocket payload.
    
    Args:
        payload: JSON data from websocket containing water level information
        
    Returns:
        Tuple of (time_points, water_levels) where:
        - time_points: List of datetime objects
        - water_levels: List of float values in meters
        
    Raises:
        ValueError: If water level data is missing from payload
    """
    # Step 1: Parse the message field (handle double-encoded JSON)
    message = payload.get("message", {})
    if isinstance(message, str):
        message = json.loads(message)  # Parse string to dict if needed
    
    # Step 2: Navigate to water_level_graph data
    # Path: message -> values -> water_level_graph -> "0"
    graph = (
        message
        .get("values", {})
        .get("water_level_graph", {})
        .get("0", {})  # "0" is the data series key
    )
    
    # Step 3: Extract value and time arrays
    values = graph.get("value", [])  # Water levels in meters
    times = graph.get("time", [])     # Unix timestamps
    
    # Step 4: Validate data exists
    if not values or not times:
        raise ValueError("water_level_graph/0/value or time is missing")
    
    # Step 5: Ensure arrays are same length (trim to shortest)
    count = min(len(values), len(times))
    values = values[:count]
    times = times[:count]
    
    # Step 6: Convert Unix timestamps to datetime objects
    time_points = [datetime.fromtimestamp(ts) for ts in times]
    
    return time_points, values


def plot_water_level(data: dict, filename: str = "station_703.png"):
    """
    Generate a water level graph and save as PNG file.
    
    Args:
        data: Websocket payload containing water level data
        filename: Output filename for the graph (default: station_703.png)
    """
    # Step 1: Extract time series data
    times, water_levels = load_water_level_graph(data)
    
    # Step 2: Extract metadata for graph title
    message = data.get("message", {})
    if isinstance(message, str):
        message = json.loads(message)
    
    code = message.get("code", "")              # Station code (e.g., "STN06")
    name = message.get("name", "")              # Station name (Thai)
    basin_name = message.get("basin", {}).get("name", "")  # Basin name
    title = f"{code} - {name} ({basin_name})"  # Combine into title
    
    # Step 3: Create figure with specific size
    plt.figure(figsize=(12, 5))  # 12 inches wide, 5 inches tall
    
    # Step 4: Plot the water level line
    plt.plot(times, water_levels, 
             linewidth=2,           # Line thickness
             color='#1f77b4',       # Blue color
             marker='',             # No markers on data points
             linestyle='-')         # Solid line
    
    # Step 5: Fill area under the line for better visualization
    plt.fill_between(times, water_levels, 
                     alpha=0.3,         # 30% transparency
                     color='#1f77b4')   # Same blue color
    
    # Step 6: Set graph labels
    plt.title(title)                    # Graph title with station info
    plt.xlabel("Time")                  # X-axis label
    plt.ylabel("Water Level (m)")       # Y-axis label
    plt.grid(True, alpha=0.3)          # Add grid with 30% transparency
    
    # Step 7: Format the datetime axis
    ax = plt.gca()  # Get current axes
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d\n%H:%M"))  # Date format
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())  # Auto-space date labels
    plt.tight_layout()  # Adjust spacing to prevent label cutoff
    
    # Step 8: Save graph to file
    plt.savefig(filename, dpi=150)  # 150 DPI for good quality
    plt.close()  # Close figure to free memory
    print(f"Graph saved to {filename}")


# ============================================================================
# IMAGE HOSTING & MESSAGING FUNCTIONS
# ============================================================================

def upload_to_imgur(filename: str) -> str:
    """
    Upload image to Cloudinary and return public URL.
    
    Args:
        filename: Path to the image file to upload
        
    Returns:
        HTTPS URL of the uploaded image
        
    Raises:
        Exception: If upload fails
    """
    try:
        # Upload image to Cloudinary with custom public_id
        upload_result = cloudinary.uploader.upload(
            filename,
            public_id=f"water_level_{os.path.basename(filename).split('.')[0]}"
        )
        
        # Extract secure HTTPS URL from response
        url = upload_result["secure_url"]
        print(f"Uploaded to Cloudinary: {url}")
        return url
        
    except Exception as e:
        raise Exception(f"Cloudinary upload failed: {str(e)}")


def send_to_line(filename: str, station_id: str):
    """
    Upload graph image and send to LINE Messaging API.
    
    Workflow:
        1. Upload image to Cloudinary (get HTTPS URL)
        2. Send image message to LINE group
        
    Args:
        filename: Path to the graph image file
        station_id: Station ID for logging purposes
    """
    # Step 1: Check if LINE sending is enabled
    send_enabled = os.getenv('SEND_TO_LINE', 'true').lower() == 'true'
    if not send_enabled:
        print(f"LINE notifications disabled (SEND_TO_LINE=false). Skipping station {station_id}")
        return
    
    # Step 2: Load LINE API credentials from environment
    line_url = os.getenv('LINE_URL')      # LINE API endpoint
    group_id = os.getenv('GROUP_ID')      # LINE group/chat ID
    api_key = os.getenv('LINE_API_KEY')   # LINE channel access token
    
    # Step 3: Validate credentials are set
    if not all([line_url, group_id, api_key]):
        print(f"Warning: LINE credentials not set. Skipping LINE notification for station {station_id}")
        return
    
    try:
        # Step 4: Upload image to Cloudinary and get URL
        image_url = upload_to_imgur(filename)
        
        # Step 5: Prepare LINE message payload
        payload = {
            "to": group_id,  # Recipient (group or user ID)
            "messages": [
                {
                    "type": "image",
                    "originalContentUrl": image_url,   # Full-size image URL
                    "previewImageUrl": image_url       # Thumbnail URL
                }
            ]
        }
        
        # Step 5: Send message to LINE API
        response = requests.post(
            line_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "X-Line-Retry-Key": str(uuid.uuid4())  # Unique key to prevent duplicates
            },
            json=payload,
            timeout=10  # 10 second timeout
        )
        
        # Step 6: Check response status
        if response.status_code == 200:
            print(f"Successfully sent {filename} to LINE (Station {station_id})")
        else:
            print(f"Failed to send to LINE: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error sending to LINE: {e}")


# ============================================================================
# WEBSOCKET & MONITORING FUNCTIONS
# ============================================================================

async def listen_and_plot(station_id: str):
    """
    Connect to water station websocket, receive data, and generate graph.
    
    Workflow:
        1. Connect to websocket for specified station
        2. Wait for data message
        3. Parse JSON data
        4. Generate water level graph
        5. Upload graph and send to LINE
        6. Wait 2 minutes and repeat
        
    Args:
        station_id: Station ID to monitor (e.g., "703", "704")
    """
    # Step 1: Build websocket URI for the station
    uri = f"wss://telerid.rid.go.th/ws/station/{station_id}/"
    
    while True:  # Run continuously
        try:
            # Step 2: Connect to websocket
            async with websockets.connect(uri) as ws:
                print(f"Connected to station {station_id}")
                
                # Step 3: Listen for messages from websocket
                async for msg in ws:
                    # Step 4: Parse JSON message
                    data = json.loads(msg)
                    print(f"Received data from station {station_id}")
                    
                    # Step 5: Handle double-encoded JSON if needed
                    if isinstance(data, str):
                        data = json.loads(data)
                    
                    # Step 6: Generate graph filename (save to /app/graphs/ for persistence)
                    filename = f"graphs/station_{station_id}.png"
                    
                    # Step 7: Create water level graph
                    plot_water_level(data, filename)
                    
                    # Step 8: Upload to Cloudinary and send to LINE
                    send_to_line(filename, station_id)
                    
                    # Step 9: Exit websocket after first message
                    break
                    
        except Exception as e:
            print(f"Error with station {station_id}: {e}")
        
        # Step 10: Wait before next update (configurable via UPDATE_INTERVAL_MINUTES)
        interval_minutes = int(os.getenv('UPDATE_INTERVAL_MINUTES', '2'))
        interval_seconds = interval_minutes * 60
        print(f"Waiting {interval_minutes} minutes before next update for station {station_id}...")
        await asyncio.sleep(interval_seconds)


async def main():
    """
    Main entry point - parse command-line arguments and monitor stations.
    
    Usage:
        python main.py              # Monitor station 703 (default)
        python main.py 703 704      # Monitor multiple stations concurrently
    """
    # Step 1: Get station IDs from command-line arguments
    # Default to ["703"] if no arguments provided
    station_ids = sys.argv[1:] if len(sys.argv) > 1 else ["703"]
    
    print(f"Monitoring stations: {', '.join(station_ids)}")
    
    # Step 2: Create async tasks for each station
    tasks = [listen_and_plot(station_id) for station_id in station_ids]
    
    # Step 3: Run all tasks concurrently and wait for completion
    await asyncio.gather(*tasks)


# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
