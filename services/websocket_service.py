"""
WebSocket Service Module
=========================
Handles websocket connections and data streaming.
"""

import asyncio
import json
import websockets
from graph.plotter import create_dashboard
from integrations.line_service import send_notification
from config.settings import get_update_interval


async def monitor_station(station_id: str):
    """
    Connect to water station websocket and generate graphs continuously.
    
    Args:
        station_id: Station ID to monitor
    """
    uri = f"wss://telerid.rid.go.th/ws/station/{station_id}/"
    
    while True:
        try:
            async with websockets.connect(uri) as ws:
                print(f"Connected to station {station_id}")
                
                async for msg in ws:
                    # Parse JSON message
                    data = json.loads(msg)
                    print(f"Received data from station {station_id}")
                    
                    # Handle double-encoded JSON
                    if isinstance(data, str):
                        data = json.loads(data)
                    
                    # Generate dashboard
                    filename = f"graphs/station_{station_id}.png"
                    create_dashboard(data, filename)
                    
                    # Send to LINE
                    send_notification(filename, station_id)
                    
                    # Exit websocket after first message
                    break
                    
        except Exception as e:
            print(f"Error with station {station_id}: {e}")
        
        # Wait before next update
        interval = get_update_interval()
        minutes = interval // 60
        print(f"Waiting {minutes} minutes before next update for station {station_id}...")
        await asyncio.sleep(interval)
