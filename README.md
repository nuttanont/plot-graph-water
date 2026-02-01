# 🌊 Water Level Monitoring System

Real-time water level monitoring system that connects to Thai government water station websockets, generates beautiful graphs, and sends automated notifications to LINE Messaging API.

## ✨ Features

- 📊 **Real-time Data Collection** - Connects to Thai water station websockets
- 📈 **Multi-Panel Dashboard** - Water level + rainfall graphs with alert zones
- 🚨 **Disaster Alerts** - Warning/critical threshold visualization (ภัยพิบัติ)
- 🌧️ **Rainfall Monitoring** - Bar charts showing precipitation data (ปริมาณน้ำฝน)
- ☁️ **Cloud Image Hosting** - Uploads graphs to Cloudinary
- 📱 **LINE Notifications** - Sends graph images to LINE groups/chats
- 🐳 **Docker Support** - Easy deployment with Docker and Docker Compose
- ⏰ **Configurable Intervals** - Set custom update frequencies
- 🔄 **Multi-Station Support** - Monitor multiple stations simultaneously
- 🌏 **Thai Character Support** - Full Unicode support for Thai text
- 📦 **Modular Architecture** - Clean folder structure for easy maintenance

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ or Docker
- LINE Messaging API credentials
- Cloudinary account (free tier available)

### Installation

#### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd plot-graph-socket

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials

# Build and run
docker-compose up -d

# View logs
docker-compose logs -f
```

#### Option 2: Local Python

```bash
# Clone the repository
git clone <your-repo-url>
cd plot-graph-socket

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run
python main.py 703
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# LINE Messaging API
GROUP_ID=your_line_group_id
LINE_API_KEY=your_line_channel_access_token
LINE_URL=https://api.line.me/v2/bot/message/push

# Cloudinary (Image Hosting)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Configuration
SEND_TO_LINE=true                # Set to 'false' to disable LINE notifications
UPDATE_INTERVAL_MINUTES=2        # Update frequency in minutes
```

### Getting API Credentials

**LINE Messaging API:**
1. Go to [LINE Developers Console](https://developers.line.biz/)
2. Create a new Messaging API channel
3. Get your Channel Access Token
4. Add your bot to a LINE group and get the Group ID

**Cloudinary:**
1. Sign up at [Cloudinary](https://cloudinary.com/users/register_free)
2. Go to your [Console](https://cloudinary.com/console)
3. Copy: Cloud Name, API Key, API Secret

## 📝 Usage

### Monitor Single Station

```bash
python main.py 703
```

### Monitor Multiple Stations

```bash
python main.py 703 704 705
```

### Docker Commands

```bash
# Start monitoring
docker-compose up -d

# View logs
docker-compose logs -f

# Stop monitoring
docker-compose down

# Rebuild after changes
docker-compose up -d --build

# Run with custom interval (5 minutes)
docker-compose run -e UPDATE_INTERVAL_MINUTES=5 water-monitor

# Test without sending to LINE
docker-compose run -e SEND_TO_LINE=false water-monitor
```

## 📂 Project Structure

```
plot-graph-socket/
├── main.py                      # Application entry point
├── config/
│   └── settings.py              # Configuration & initialization
├── graph/
│   ├── data_processor.py        # Data extraction from websocket
│   └── plotter.py               # Multi-panel graph generation
├── integrations/
│   ├── cloudinary_service.py    # Image upload to Cloudinary
│   └── line_service.py          # LINE notification sending
├── services/
│   └── websocket_service.py     # WebSocket connection handling
├── import_matplotlib.py         # Standalone graph generator (from JSON)
├── import_asyncio.py            # Websocket listener example
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker image configuration
├── docker-compose.yml           # Docker Compose configuration
├── .env                         # Environment variables (not in git)
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── DEPLOYMENT.md                # Detailed deployment guide
├── README.md                    # This file
├── graphs/                      # Generated graph images (auto-created)
└── response-*.json              # Sample data files
```

## 🐳 Docker Deployment

The project includes complete Docker support with:

- **Multi-stage builds** for optimal image size
- **Thai font support** for proper character rendering
- **Volume mounting** for persistent graph storage
- **Configurable restart policies**
- **Environment variable support**

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions including:
- Fly.io (free tier)
- Railway
- DigitalOcean
- Oracle Cloud
- Azure Container Instances

## 🎨 Features in Detail

### Graph Generation

- **Multi-panel dashboard** (2 subplots: water level + rainfall)
- **Water level graph** with continuous line and filled areas
- **Alert zones** with color-coded thresholds:
  - 🟡 **Warning zone** (เฝ้าระวัง) - Orange
  - 🔴 **Critical zone** (วิกฤต) - Red
- **Rainfall bar chart** showing precipitation events
- **Time-series data** with proper datetime formatting
- **Station information** in title (code, name, basin)
- **High-quality output** (150 DPI, 14"×10" dashboard)
- **Thai + English labels** with proper font rendering

### Monitoring

- **Real-time websocket connections** to Thai water stations
- **Automatic reconnection** on connection failures
- **Configurable update intervals** (default: 2 minutes)
- **Multi-station support** with concurrent processing
- **Error handling** and logging

### Notifications

- **Image messages** sent to LINE groups
- **Cloudinary hosting** for reliable image delivery
- **Retry mechanisms** to prevent duplicate messages
- **Toggle notifications** for testing (SEND_TO_LINE=false)

## 🛠️ Development

### Running Tests

```bash
# Test graph generation from sample data
python import_matplotlib.py

# Test websocket connection
python import_asyncio.py

# Test with LINE disabled
SEND_TO_LINE=false python main.py 703
```

### Code Structure

Modular architecture with clear separation of concerns:

**main.py** - Application entry point (37 lines)
- Initializes configurations
- Orchestrates monitoring tasks

**config/settings.py** - Configuration module
- Environment variable loading
- Cloudinary initialization
- Matplotlib font configuration

**graph/** - Graph generation modules
- `data_processor.py` - Extract data from websocket JSON
- `plotter.py` - Create multi-panel dashboards

**integrations/** - External service integrations
- `cloudinary_service.py` - Image upload to cloud
- `line_service.py` - LINE notification sending

**services/** - Core services
- `websocket_service.py` - WebSocket connection management

## 🐛 Troubleshooting

### Thai Characters Not Displaying

```bash
# Rebuild Docker image with font support
docker-compose build --no-cache
docker-compose up
```

### LINE Notifications Not Working

1. Check `.env` file has correct credentials
2. Verify `SEND_TO_LINE=true`
3. Check LINE API token is valid
4. Verify bot is added to the group

### Graphs Not Saving

1. Ensure `graphs/` directory exists
2. Check Docker volume mount: `./graphs:/app/graphs`
3. Verify write permissions

### Font Warnings in Docker

The Dockerfile installs comprehensive font support. If you still see warnings:
```bash
docker-compose build --no-cache
```

### Module Import Errors

If you get `ModuleNotFoundError` after restructuring:

1. **Docker:** Rebuild container
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

2. **Local:** Ensure you're in the project root
```bash
cd /path/to/plot-graph-socket
python main.py 703
```

## 📊 Monitoring Multiple Stations

Edit `docker-compose.yml`:

```yaml
command: python main.py 701 702 703 704 705 706
```

Each station will:
- Run in parallel
- Generate separate graphs
- Send independent notifications
- Update at the configured interval

## 🔒 Security

- ✅ **API keys** stored in `.env` (excluded from git)
- ✅ **Secure HTTPS** connections only
- ✅ **No credentials** in code or logs
- ✅ **Docker secrets** support available

## 📄 License

MIT License - feel free to use for your own projects!

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues or questions:
1. Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment help
2. Review troubleshooting section above
3. Open an issue on GitHub

## 🙏 Acknowledgments

- Thai government water station API
- LINE Messaging API
- Cloudinary image hosting
- Matplotlib for graph generation
- Docker for containerization

---

**Made with ❤️ for water level monitoring in Thailand** 🇹🇭
