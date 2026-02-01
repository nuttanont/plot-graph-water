"""
Graph Plotting Module
=====================
Generates multi-panel dashboard graphs.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from .data_processor import extract_water_level_graph, extract_rainfall_graph, extract_station_info


def create_dashboard(data: dict, filename: str):
    """
    Generate a multi-panel dashboard with water level, rainfall, and alerts.
    
    Creates 2 subplots:
    1. Water Level with warning/critical thresholds
    2. Rainfall bar chart
    
    Args:
        data: Websocket payload containing all data
        filename: Output filename for the graph
    """
    # Extract all data
    station = extract_station_info(data)
    wl_times, wl_values = extract_water_level_graph(data)
    rain_times, rain_values = extract_rainfall_graph(data)
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    fig.suptitle(
        f"{station['code']} - {station['name']} ({station['basin_name']})", 
        fontsize=16, 
        fontweight='bold'
    )
    
    # Plot water level panel
    _plot_water_level_panel(ax1, wl_times, wl_values, station)
    
    # Plot rainfall panel
    _plot_rainfall_panel(ax2, rain_times, rain_values)
    
    # Save figure
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Dashboard saved to {filename}")


def _plot_water_level_panel(ax, times, values, station):
    """Plot water level with alert zones."""
    warning = station['warning_level']
    critical = station['critical_level']
    
    # Main water level line
    ax.plot(times, values, 
            linewidth=2.5, 
            color='#2E86AB',
            label='ระดับน้ำ (Water Level)',
            zorder=3)
    
    ax.fill_between(times, values, alpha=0.3, color='#2E86AB')
    
    # Warning threshold
    if warning:
        ax.axhline(y=warning, 
                  color='#F77F00', 
                  linestyle='--', 
                  linewidth=2,
                  label=f'ระดับเฝ้าระวัง ({warning}m)',
                  zorder=2)
        
        if critical:
            ax.fill_between(times, warning, critical,
                          alpha=0.15,
                          color='#F77F00',
                          label='เขตเฝ้าระวัง')
    
    # Critical threshold
    if critical:
        ax.axhline(y=critical, 
                  color='#D62828', 
                  linestyle='--', 
                  linewidth=2,
                  label=f'ระดับวิกฤต ({critical}m)',
                  zorder=2)
        
        y_max = max(max(values) if values else critical, critical * 1.1)
        ax.fill_between(times, critical, y_max,
                      alpha=0.15,
                      color='#D62828',
                      label='เขตวิกฤต')
    
    # Styling
    ax.set_ylabel("ระดับน้ำ (m)", fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)
    ax.legend(loc='upper left', framealpha=0.9, fontsize=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d\n%H:%M"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())


def _plot_rainfall_panel(ax, times, values):
    """Plot rainfall bar chart."""
    if times and values:
        # Filter non-zero rainfall
        non_zero = [(t, v) for t, v in zip(times, values) if v > 0]
        
        if non_zero:
            # Show recent 100 events
            recent = non_zero[-100:]
            filtered_times, filtered_values = zip(*recent)
            
            ax.bar(filtered_times, filtered_values,
                  width=0.02,
                  color='#06A77D',
                  alpha=0.7,
                  edgecolor='#05846A',
                  linewidth=0.8)
            
            ax.set_ylabel("ปริมาณน้ำฝน (mm)", fontsize=12, fontweight='bold')
            ax.set_xlabel("เวลา (Time)", fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y', linestyle=':', linewidth=0.8)
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d\n%H:%M"))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            return
    
    # No data case
    ax.text(0.5, 0.5, 'ไม่มีข้อมูลฝน (No Rainfall Data)', 
           ha='center', va='center', 
           transform=ax.transAxes,
           fontsize=14, color='gray')
    ax.set_ylabel("ปริมาณน้ำฝน (mm)", fontsize=12, fontweight='bold')
    ax.set_xlabel("เวลา (Time)", fontsize=12, fontweight='bold')
