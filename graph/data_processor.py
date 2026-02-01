"""
Data Processing Module
======================
Extracts and processes data from websocket payloads.
"""

import json
from datetime import datetime


def parse_message(payload: dict) -> dict:
    """
    Parse message field (handle double-encoded JSON).
    
    Args:
        payload: Raw websocket payload
        
    Returns:
        Parsed message dictionary
    """
    message = payload.get("message", {})
    if isinstance(message, str):
        message = json.loads(message)
    return message


def extract_water_level_graph(payload: dict) -> tuple[list[datetime], list[float]]:
    """
    Extract water level graph data from websocket payload.
    
    Args:
        payload: JSON data from websocket
        
    Returns:
        Tuple of (time_points, water_levels)
    """
    message = parse_message(payload)
    
    graph = (
        message
        .get("values", {})
        .get("water_level_graph", {})
        .get("0", {})
    )
    
    values = graph.get("value", [])
    times = graph.get("time", [])
    
    if not values or not times:
        raise ValueError("water_level_graph data is missing")
    
    count = min(len(values), len(times))
    time_points = [datetime.fromtimestamp(ts) for ts in times[:count]]
    
    return time_points, values[:count]


def extract_rainfall_graph(payload: dict) -> tuple[list[datetime], list[float]]:
    """
    Extract rainfall graph data from websocket payload.
    
    Args:
        payload: JSON data from websocket
        
    Returns:
        Tuple of (time_points, rainfall_values) in mm
    """
    message = parse_message(payload)
    
    rain_data = message.get("values", {}).get("rain_graph", {})
    values = rain_data.get("value", [])
    times = rain_data.get("time", [])
    
    if not values or not times:
        return [], []
    
    count = min(len(values), len(times))
    time_points = [datetime.fromtimestamp(ts) for ts in times[:count]]
    
    return time_points, values[:count]


def extract_station_info(payload: dict) -> dict:
    """
    Extract station metadata from payload.
    
    Args:
        payload: JSON data from websocket
        
    Returns:
        Dictionary with station info: code, name, basin_name, warning_level, critical_level
    """
    message = parse_message(payload)
    
    return {
        'code': message.get("code", ""),
        'name': message.get("name", ""),
        'basin_name': message.get("basin", {}).get("name", ""),
        'warning_level': message.get("water_level_warning"),
        'critical_level': message.get("water_level_critical")
    }
