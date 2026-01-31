# Water Level Monitor - Deployment Guide

## 🐳 Docker Deployment

### Local Testing

**1. Build and run with Docker:**
```bash
docker build -t water-monitor .
docker run --env-file .env water-monitor
```

**2. Or use Docker Compose:**
```bash
docker-compose up -d
docker-compose logs -f
```

---

## ☁️ Cloud Deployment Options

### Option 1: Fly.io (Recommended - Easiest)

**1. Install Fly CLI:**
```bash
curl -L https://fly.io/install.sh | sh
```

**2. Login and launch:**
```bash
fly auth login
fly launch
```

**3. Set environment variables:**
```bash
fly secrets set GROUP_ID=your_group_id
fly secrets set LINE_API_KEY=your_line_api_key
fly secrets set LINE_URL=https://api.line.me/v2/bot/message/push
fly secrets set CLOUDINARY_CLOUD_NAME=your_cloud_name
fly secrets set CLOUDINARY_API_KEY=your_api_key
fly secrets set CLOUDINARY_API_SECRET=your_api_secret
```

**4. Deploy:**
```bash
fly deploy
```

---

### Option 2: Railway

**1. Install Railway CLI:**
```bash
npm install -g @railway/cli
```

**2. Login and init:**
```bash
railway login
railway init
```

**3. Add environment variables in Railway dashboard:**
- Go to https://railway.app/dashboard
- Add all your .env variables

**4. Deploy:**
```bash
railway up
```

---

### Option 3: DigitalOcean Droplet

**1. Create a $4/month droplet (Ubuntu 22.04)**

**2. SSH into your droplet:**
```bash
ssh root@your_droplet_ip
```

**3. Install Docker:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

**4. Clone your repo and deploy:**
```bash
git clone <your-repo-url>
cd plot-graph-socket
nano .env  # Add your credentials
docker-compose up -d
```

---

### Option 4: Oracle Cloud Free Tier

**1. Create Oracle Cloud account and VM instance**

**2. SSH into instance:**
```bash
ssh ubuntu@instance_ip
```

**3. Install Docker:**
```bash
sudo apt update
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker ubuntu
```

**4. Deploy:**
```bash
git clone <your-repo-url>
cd plot-graph-socket
nano .env  # Add credentials
docker-compose up -d
```

---

## 🔄 Continuous Monitoring

To keep the script running continuously (remove the `break` statement):

Edit `main.py` line ~176:
```python
# Remove or comment out this line:
# break
```

Then rebuild:
```bash
docker-compose up -d --build
```

---

## 📊 Check Logs

**Docker Compose:**
```bash
docker-compose logs -f
```

**Fly.io:**
```bash
fly logs
```

**Railway:**
```bash
railway logs
```

---

## 🛑 Stop Service

**Docker Compose:**
```bash
docker-compose down
```

**Fly.io:**
```bash
fly scale count 0
```

---

## 💰 Cost Estimates

- **Fly.io:** Free tier (3 shared VMs)
- **Railway:** $5/month (includes $5 credit)
- **DigitalOcean:** $4-6/month
- **Oracle Cloud:** FREE forever (2 ARM VMs)

---

## 🔧 Customize Station IDs

Edit `docker-compose.yml`:
```yaml
command: python main.py 703 704 705 706  # Add your station IDs
```
