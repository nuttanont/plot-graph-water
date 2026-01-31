# ============================================================================
# Water Level Monitoring System - Docker Image
# ============================================================================
# Base: Python 3.11 Slim (minimal Debian-based image)
# Features: Thai font support, UTF-8 encoding, matplotlib optimization
# ============================================================================

FROM python:3.11-slim

# ----------------------------------------------------------------------------
# ENVIRONMENT CONFIGURATION
# ----------------------------------------------------------------------------
# Set UTF-8 locale for proper Thai character encoding
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONIOENCODING=utf-8

# Set working directory inside container
WORKDIR /app

# ----------------------------------------------------------------------------
# SYSTEM DEPENDENCIES
# ----------------------------------------------------------------------------
# Install required packages:
# - gcc: Required for compiling Python packages
# - locales: Provides UTF-8 locale support
# - fonts-tlwg-*: Thai Linux Working Group fonts (Thai character support)
# - fonts-noto*: Google's Noto fonts for additional coverage
# - fonts-dejavu-core: Fallback font with good Unicode coverage
# - fontconfig: Font configuration and caching system
RUN apt-get update && apt-get install -y \
    gcc \
    locales \
    fonts-tlwg-laksaman \
    fonts-tlwg-sawasdee \
    fonts-noto \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    fonts-dejavu-core \
    fontconfig \
    # Configure UTF-8 locale
    && sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen en_US.UTF-8 \
    # Rebuild font cache for matplotlib
    && fc-cache -fv \
    # Clean up to reduce image size
    && rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------------------------
# PYTHON DEPENDENCIES
# ----------------------------------------------------------------------------
# Copy requirements.txt first (Docker layer caching optimization)
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Force matplotlib to rebuild font cache with newly installed fonts
RUN rm -rf /root/.cache/matplotlib \
    && python -c "import matplotlib.pyplot as plt; import matplotlib.font_manager as fm; fm._load_fontmanager(try_read_cache=False)"

# ----------------------------------------------------------------------------
# APPLICATION CODE
# ----------------------------------------------------------------------------
# Copy Python script and environment variables
COPY main.py .
COPY .env .

# Create directory for graph output (will be mounted as volume)
RUN mkdir -p /app/graphs

# ----------------------------------------------------------------------------
# RUNTIME
# ----------------------------------------------------------------------------
# Default command (can be overridden in docker-compose.yml)
CMD ["python", "main.py", "703"]
