# EC2 deployment (Ubuntu 22.04+)

This sets up the FastAPI app with Gunicorn (Uvicorn workers), Nginx, and systemd. Celery/Redis is not used.

## 1) Provision the server
- Ubuntu 22.04 LTS EC2 instance
- Security Group: open 80 (HTTP) and 443 (HTTPS). Optionally 22 (SSH) for admin.
- Point your domain DNS A record to the instance IP (optional but recommended).

## 2) Base packages
```bash
sudo apt update
sudo apt install -y git nginx python3-pip python3-venv
# PDF (weasyprint) runtime libs; skip if not using PDF export
sudo apt install -y libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libffi8
```

## 3) Clone project & create venv
```bash
sudo mkdir -p /opt/ija_ai_backend
sudo chown $USER:$USER /opt/ija_ai_backend
cd /opt/ija_ai_backend
# If using GitHub
git clone https://github.com/Ankit-s0ni/ija_ai_backend .
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel
pip install -r requirements.txt
```

## 4) Environment variables
- Create a production env file (never commit this):
```bash
sudo mkdir -p /etc/ija_api
sudo nano /etc/ija_api/.env
```
Paste values (see `.env.example`):
- Set BACKEND_CORS_ORIGINS to your front-end origin(s)
- Use a strong SECRET_KEY
- Keep MongoDB Atlas creds
	(No Redis required)

## 5) Systemd services
Copy unit files and enable them.

```bash
sudo cp deploy/systemd/ija-api.service /etc/systemd/system/ija-api.service

sudo systemctl daemon-reload
sudo systemctl enable ija-api
sudo systemctl start ija-api

# Check status
systemctl status ija-api --no-pager
journalctl -u ija-api -n 100 --no-pager
```

## 6) Nginx reverse proxy
```bash
sudo cp deploy/nginx/ija_api.conf /etc/nginx/sites-available/ija_api
sudo ln -s /etc/nginx/sites-available/ija_api /etc/nginx/sites-enabled/ija_api
# Remove default site if present
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

Nginx listens on 80 and proxies to Gunicorn on 127.0.0.1:8000.

### HTTPS (optional but recommended)
If you have a domain pointed to the server:
```bash
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
sudo certbot --nginx -d api.yourdomain.com
```

## 7) Updates & deploys
```bash
cd /opt/ija_ai_backend
source .venv/bin/activate
git pull
pip install -r requirements.txt
sudo systemctl restart ija-api
```

## 8) Health check
- http://YOUR_SERVER/health should return `{ "status": "ok", ... }`

## Paths used by unit files
- App root: /opt/ija_ai_backend
- Venv: /opt/ija_ai_backend/.venv
- Env file: /etc/ija_api/.env
- App module: app.main:app

Adjust these to your preferences if you deploy elsewhere.
