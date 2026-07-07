# Guide de Déploiement Ubuntu (Gunicorn + Nginx)

## 1. Préparer le serveur
```bash
sudo apt update
sudo apt install python3-pip python3-venv postgresql nginx git
```

## 2. Configurer PostgreSQL
```bash
sudo -u postgres psql
CREATE DATABASE dbaescttresoreire;
CREATE USER association_user WITH PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE dbaescttresoreire TO association_user;
\q
```

## 3. Configurer l'application
```bash
cd /var/www
git clone <votre_repo>
cd Application-tr-sori-re-AESCT-2026
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env # Éditer avec DATABASE_URL=postgresql://association_user:votre_mot_de_passe@localhost/dbaescttresoreire
python seed.py
```

## 4. Configurer Gunicorn (Systemd)
Créer `/etc/systemd/system/association.service` :
```ini
[Unit]
Description=Gunicorn instance to serve Association Trésorerie
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/Application-tr-sori-re-AESCT-2026
Environment="PATH=/var/www/Application-tr-sori-re-AESCT-2026/venv/bin"
ExecStart=/var/www/Application-tr-sori-re-AESCT-2026/venv/bin/gunicorn --workers 3 --bind unix:app.sock wsgi:app

[Install]
WantedBy=multi-user.target
```

## 5. Configurer Nginx
Créer `/etc/nginx/sites-available/association` :
```nginx
server {
    listen 80;
    server_name votre_domaine.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/Application-tr-sori-re-AESCT-2026/app.sock;
    }

    location /static {
        alias /var/www/Application-tr-sori-re-AESCT-2026/static;
    }
}
```
Activer le site :
```bash
sudo ln -s /etc/nginx/sites-available/association /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl start association
sudo systemctl enable association
```
