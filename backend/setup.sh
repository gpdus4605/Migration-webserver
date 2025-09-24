#!/bin/bash
# EC2 User-Data Script
set -e
sudo timedatectl set-timezone 'Asia/Seoul'


# --- 1. Install Dependencies (run as root) ---
echo "### Updating packages and installing dependencies..."
apt-get update -y
apt-get install -y git curl ca-certificates

echo "### Installing Docker..."
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start and enable Docker service
echo "### Starting and enabling Docker service..."
systemctl start docker
systemctl enable docker

# Add ubuntu user to docker group for later use (e.g. CI/CD)
usermod -aG docker ubuntu || true

echo "### Docker installed and started successfully."

# --- 2. Clone Repository & Run Setup (as root) ---
# Work in the ubuntu user's home directory
cd /home/ubuntu

# Environment Variables
export DOMAIN_NAME="www.gpdus4605.site"
export CERTBOT_EMAIL="gpdus4605@naver.com"
export GITHUB_REPO_URL="https://github.com/gpdus4605/Migration-webserver"
PROJECT_DIR="Migration-webserver"

# Git Clone
echo "### Cloning repository..."
git clone "$GITHUB_REPO_URL" "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create .env file
echo "### Creating .env file..."
cat <<EOF > .env
# PostgreSQL 데이터베이스 설정
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=mydatabase

# 외부 접속 포트 설정
WEB_PORT=80
DB_PORT=5433

JWT_SECRET_KEY=my-super-secret-key-for-docker-in-env-file
FLASK_APP=run.py
EOF

echo "### .env file created successfully."

# Docker Compose and Certbot
echo "### SSL certificate issuance process skipped (handled by AWS ACM/CloudFront)."
# cp backend/nginx/certbot.conf backend/nginx/default.conf
#
# echo "### Starting temporary Nginx..."
# docker compose -f backend/docker-compose.yml up -d nginx
#
# echo "### Issuing SSL certificate..."
# docker run --rm \
#   -v "/etc/letsencrypt:/etc/letsencrypt" \
#   -v "/var/www/certbot:/var/www/certbot" \
#   certbot/certbot certonly --webroot -w /var/www/certbot --force-renewal \
#   --email "${CERTBOT_EMAIL}" -d "${DOMAIN_NAME}" --agree-tos -n
#
# echo "### Finalizing Nginx configuration..."
# docker compose -f backend/docker-compose.yml down
# rm backend/nginx/default.conf

cp backend/nginx/default.conf.prod backend/nginx/default.conf

# Force remove existing certbot container to avoid name conflict
echo "### Removing conflicting certbot container if it exists..."
docker rm -f my-certbot || true

echo "### Starting all services..."
docker compose -f backend/docker-compose.yml up -d

# --- 3. Set Ownership for ubuntu user ---
echo "### Changing ownership to ubuntu user..."
chown -R ubuntu:ubuntu /home/ubuntu/$PROJECT_DIR

echo "### Initial setup finished successfully!"
