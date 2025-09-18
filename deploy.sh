#!/bin/bash
# 스크립트 실행 중 오류가 발생하면 즉시 중단합니다.
set -e

# GitHub Actions에서 환경 변수로 전달된 값들을 사용합니다.

# 배포 디렉터리로 이동합니다. (없으면 생성)
if [ ! -d "onpremise/.git" ]; then
  # GITHUB_REPOSITORY는 '소유자/리포지토리명' 형태입니다. (예: CloudDx/hyeyeon)
  git clone https://github.com/${GITHUB_REPOSITORY} "onpremise"
fi
cd onpremise
git pull origin main

# .env 파일 생성
echo "### Creating .env file..."
cat << EOF > .env
${ENV_FILE_CONTENT}
EOF

# Docker Compose V2 설치
echo "### Installing Docker Compose V2..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

# SSL 인증서 발급 (필요시)
if [ ! -d "/etc/letsencrypt/live/${DOMAIN_NAME}" ]; then
  echo "### SSL certificate not found. Issuing new certificate..."
  
  # 1. 임시 Nginx 실행
  sudo /usr/local/bin/docker-compose down --remove-orphans
  sudo cp nginx/default.conf.pre nginx/default.conf
  sudo /usr/local/bin/docker-compose up -d nginx

  # 2. Certbot 실행
  sudo docker run --rm \
    -v "/etc/letsencrypt:/etc/letsencrypt" \
    -v "/var/www/certbot:/var/www/certbot" \
    certbot/certbot certonly --webroot -w /var/www/certbot --force-renewal \
    --email ${CERTBOT_EMAIL} -d ${DOMAIN_NAME} --agree-tos -n
  
  # 3. 임시 Nginx 정리
  sudo /usr/local/bin/docker-compose down
  git checkout HEAD -- nginx/default.conf
fi

# 4. 모든 서비스 재기동
sudo /usr/local/bin/docker-compose up -d --force-recreate --remove-orphans

# DB 마이그레이션
sudo /usr/local/bin/docker-compose exec api flask db upgrade

# 불필요한 Docker 이미지 정리
sudo docker image prune -f

