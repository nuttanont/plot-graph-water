"""
LINE Messaging Service Module
==============================
Handles LINE notification sending.
"""

import os
import uuid
import requests
from .cloudinary_service import upload_image


def send_notification(filename: str, station_id: str):
    """
    Upload graph image and send to LINE Messaging API.
    
    Args:
        filename: Path to the graph image file
        station_id: Station ID for logging
    """
    from config.settings import is_line_enabled
    
    # Check if LINE is enabled
    if not is_line_enabled():
        print(f"LINE notifications disabled. Skipping station {station_id}")
        return
    
    # Load credentials
    line_url = os.getenv('LINE_URL')
    group_id = os.getenv('GROUP_ID')
    api_key = os.getenv('LINE_API_KEY')
    
    if not all([line_url, group_id, api_key]):
        print(f"Warning: LINE credentials not set. Skipping station {station_id}")
        return
    
    try:
        # Upload to Cloudinary
        image_url = upload_image(filename)
        
        # Prepare LINE message
        payload = {
            "to": group_id,
            "messages": [
                {
                    "type": "image",
                    "originalContentUrl": image_url,
                    "previewImageUrl": image_url
                }
            ]
        }
        
        # Send to LINE
        response = requests.post(
            line_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "X-Line-Retry-Key": str(uuid.uuid4())
            },
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"Successfully sent {filename} to LINE (Station {station_id})")
        else:
            print(f"Failed to send to LINE: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error sending to LINE: {e}")
