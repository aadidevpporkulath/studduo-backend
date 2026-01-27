# StudduoAI Backend Deployment Guide

## 🚀 Quick Deployment Steps

### 1. Connect to Your VPS
```bash
ssh root@your_vps_ip
```

### 2. Upload Project Files
From your local machine:
```bash
# Option A: Using SCP
scp -r C:\Users\aadid\Work\studduoai\backend root@your_vps_ip:/tmp/

# Option B: Using Git (recommended)
# First push your code to GitHub, then on VPS:
git clone https://github.com/yourusername/studduoai.git
```

### 3. Run Deployment Script
```bash
cd /tmp/backend  # or your cloned directory
chmod +x deploy.sh setup_services.sh
sudo bash deploy.sh
```

### 4. Configure Environment
```bash
cd /var/www/studduoai

# Copy and edit environment variables
cp .env.production .env
nano .env  # Fill in your API keys and credentials

# Upload Firebase credentials
# (scp firebase-credentials.json from local machine)
```

### 5. Upload Knowledge Base
```bash
# From local machine:
scp -r C:\Users\aadid\Work\studduoai\backend\knowledge\* root@your_vps_ip:/var/www/studduoai/knowledge/
```

### 6. Initialize Vector Store (if needed)
```bash
cd /var/www/studduoai
source venv/bin/activate
python ingest_documents.py
```

### 7. Start Services
```bash
sudo bash setup_services.sh
```

### 8. Set Up SSL (Optional but Recommended)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com
```

## 📊 Monitoring & Management

### Check Application Logs
```bash
# Real-time logs
sudo journalctl -u studduoai -f

# Last 100 lines
sudo journalctl -u studduoai -n 100

# Application logs
tail -f /var/www/studduoai/logs/error.log
tail -f /var/www/studduoai/logs/access.log
```

### Service Management
```bash
# Restart application
sudo systemctl restart studduoai

# Check status
sudo systemctl status studduoai

# Stop application
sudo systemctl stop studduoai

# Start application
sudo systemctl start studduoai
```

### Nginx Management
```bash
# Test configuration
sudo nginx -t

# Reload configuration
sudo systemctl reload nginx

# Restart Nginx
sudo systemctl restart nginx

# Check logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

## 🔧 Troubleshooting

### Application won't start
```bash
# Check logs
sudo journalctl -u studduoai -n 50

# Common issues:
# 1. Missing .env file
# 2. Wrong Python path in systemd service
# 3. Missing dependencies
# 4. Port already in use
```

### Can't access API
```bash
# Check if app is running
curl http://localhost:8000/health

# Check firewall
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check Nginx
sudo nginx -t
sudo systemctl status nginx
```

### Memory issues
```bash
# Check memory usage
free -h

# Check process memory
ps aux --sort=-%mem | head

# Reduce workers if needed (edit systemd service)
sudo nano /etc/systemd/system/studduoai.service
# Change --workers value to 1
sudo systemctl daemon-reload
sudo systemctl restart studduoai
```

## 🔄 Updating the Application

```bash
cd /var/www/studduoai

# Pull latest changes (if using Git)
git pull

# Or upload new files via SCP

# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart studduoai
```

## 🔒 Security Checklist

- [ ] Set up firewall (UFW)
- [ ] Install SSL certificate (Let's Encrypt)
- [ ] Disable root SSH login
- [ ] Set up SSH key authentication
- [ ] Enable automatic security updates
- [ ] Set proper file permissions
- [ ] Configure fail2ban
- [ ] Regular backups enabled

## 📈 Performance Optimization

1. **Enable HTTP/2 in Nginx** (after SSL setup)
2. **Configure Nginx caching** for static content
3. **Monitor with htop** or install monitoring tools
4. **Set up log rotation** to prevent disk fill
5. **Consider Redis** for session caching (future)

## 🆘 Support

If you encounter issues:
1. Check application logs
2. Check Nginx error logs
3. Verify .env configuration
4. Ensure all credentials are correct
5. Check system resources (RAM, disk space)
