"""
Water Level Monitoring System
==============================
Main entry point for the application.

Usage:
    python main.py              # Monitor station 703 (default)
    python main.py 703 704      # Monitor multiple stations concurrently
"""

import asyncio
import sys
from config.settings import init_cloudinary, init_matplotlib
from services.websocket_service import monitor_station


async def main():
    """Initialize application and start monitoring."""
    # Initialize configurations
    print("Initializing configurations...")
    init_cloudinary()
    init_matplotlib()
    
    # Get station IDs from command-line arguments
    station_ids = sys.argv[1:] if len(sys.argv) > 1 else ["703"]
    print(f"Monitoring stations: {', '.join(station_ids)}")
    
    # Create monitoring tasks
    tasks = [monitor_station(station_id) for station_id in station_ids]
    
    # Run all tasks concurrently
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
