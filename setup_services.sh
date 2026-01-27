#!/bin/bash

# Service Setup Script
# Run this AFTER deploy.sh and setting up .env

set -e

APP_DIR="/var/www/studduoai"
DOMAIN="your_domain_or_ip"  # Change this to your domain or server IP

echo "🔧 Setting up services..."

# Ensure logs directory exists with proper permissions
echo "📁 Setting up logs directory..."
mkdir -p $APP_DIR/logs
chmod 755 $APP_DIR/logs

# Create Gunicorn systemd service
echo "📝 Creating systemd service..."
sudo tee /etc/systemd/system/studduoai.service > /dev/null << EOF
[Unit]
Description=StudduoAI FastAPI Application
After=network.target

[Service]
Type=notify
User=$USER
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn main:app \\
    --workers 2 \\
    --worker-class uvicorn.workers.UvicornWorker \\
    --bind 127.0.0.1:8000 \\
    --timeout 120 \\
    --access-logfile $APP_DIR/logs/access.log \\
    --error-logfile $APP_DIR/logs/error.log \\
    --log-level info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Install Gunicorn if not already installed
echo "📦 Installing Gunicorn..."
source $APP_DIR/venv/bin/activate
pip install gunicorn

# Create Nginx configuration
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/studduoai > /dev/null << 'EOF'
server {
    listen 80;
    server_name $DOMAIN;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /health {
        access_log off;
        return 200 "healthy\n";
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/studduoai /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo "🧪 Testing Nginx configuration..."
sudo nginx -t

# Enable and start services
echo "▶️  Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable studduoai
sudo systemctl start studduoai
sudo systemctl restart nginx

# Check service status
echo ""
echo "📊 Service Status:"
sudo systemctl status studduoai --no-pager

echo ""
echo "✅ Setup complete!"
echo ""
echo "🔍 Useful commands:"
echo "  Check logs: sudo journalctl -u studduoai -f"
echo "  Restart app: sudo systemctl restart studduoai"
echo "  Check status: sudo systemctl status studduoai"
echo "  Nginx logs: sudo tail -f /var/log/nginx/error.log"
echo ""
echo "🌐 Your API should be accessible at: http://$DOMAIN"
echo ""
echo "🔒 Next: Set up SSL with Let's Encrypt:"
echo "  sudo apt install certbot python3-certbot-nginx -y"
echo "  sudo certbot --nginx -d $DOMAIN"
