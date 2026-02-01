"""
Configuration Module
====================
Handles environment variables and application settings.
"""

import os
from dotenv import load_dotenv
import cloudinary
import matplotlib
import matplotlib.font_manager as fm

# Load environment variables
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(script_dir, '.env')
load_dotenv(env_path)


def init_cloudinary():
    """Initialize Cloudinary configuration."""
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET'),
        secure=True
    )


def init_matplotlib():
    """Configure matplotlib for Thai character support."""
    matplotlib.use('Agg')
    fm._load_fontmanager(try_read_cache=False)
    
    import matplotlib.pyplot as plt
    
    # Auto-detect available Thai fonts, fall back gracefully on Mac
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    # Priority: Thai fonts (Docker) -> System fonts (Mac)
    font_candidates = ['Laksaman', 'Sawasdee New', 'Arial Unicode MS', 'DejaVu Sans', 'sans-serif']
    selected_fonts = [font for font in font_candidates if font in available_fonts or font == 'sans-serif']
    
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = selected_fonts
    plt.rcParams['axes.unicode_minus'] = False
    
    matplotlib.rcParams['pdf.fonttype'] = 42
    matplotlib.rcParams['ps.fonttype'] = 42


def get_update_interval() -> int:
    """Get update interval in seconds from environment."""
    interval_minutes = int(os.getenv('UPDATE_INTERVAL_MINUTES', '2'))
    return interval_minutes * 60


def is_line_enabled() -> bool:
    """Check if LINE notifications are enabled."""
    return os.getenv('SEND_TO_LINE', 'true').lower() == 'true'
