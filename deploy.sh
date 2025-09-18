#!/bin/bash
# 스크립트 실행 중 오류가 발생하면 즉시 중단합니다.
set -e
 
# GitHub Actions에서 전달된 환경 변수를 사용합니다.
# working-directory가 /home/ubuntu 이므로, onpremise 디렉터리를 기준으로 작업합니다.
 
echo "### Cloning/Pulling repository..."
if [ ! -d "onpremise" ]; then
  # GITHUB_REPOSITORY는 'CloudDx/hyeyeon'과 같은 형태입니다.
  # git clone 시 HTTPS 주소에 인증 정보가 필요할 수 있으므로, Personal Access Token(PAT)을 사용하는 것이 더 안정적입니다.
  # 여기서는 간단하게 공개 리포지토리로 가정합니다.
  git clone https://github.com/${GITHUB_REPOSITORY} onpremise
fi
 
cd onpremise
git pull origin main

# .env 파일 생성
echo "### Creating .env file..."
# Base64로 인코딩된 ENV_FILE_CONTENT를 디코딩하여 .env 파일을 생성합니다.
echo "$ENV_FILE_CONTENT" | base64 -d > .env

# SSL 인증서 발급 (필요시)
# Docker Compose V2는 docker compose (하이픈 없음) 명령어를 사용합니다.
# ubuntu 사용자는 보통 sudo 없이 docker 명령을 실행할 수 있도록 설정되어 있습니다.
# 만약 권한 오류가 발생하면 아래 명령어들 앞에 sudo를 붙여주세요.
echo "### Checking for SSL certificate..."
if [ ! -d "/etc/letsencrypt/live/${DOMAIN_NAME}" ]; then
  echo "### SSL certificate not found. Issuing new certificate..."
  
  # 1. 임시 Nginx 실행
  docker compose down --remove-orphans
  cp nginx/default.conf.pre nginx/default.conf
  docker compose up -d nginx

  # 2. Certbot 실행
  docker run --rm \
    -v "/etc/letsencrypt:/etc/letsencrypt" \
    -v "/var/www/certbot:/var/www/certbot" \
    certbot/certbot certonly --webroot -w /var/www/certbot --force-renewal \
    --email ${CERTBOT_EMAIL} -d ${DOMAIN_NAME} --agree-tos -n
  
  # 3. 임시 Nginx 정리
  docker compose down
  git checkout HEAD -- nginx/default.conf
fi

# 4. 모든 서비스 재기동
echo "### Restarting all services..."
docker compose up -d --build --force-recreate --remove-orphans

# DB 마이그레이션
echo "### Running database migrations..."
docker compose exec api flask db upgrade

# 불필요한 Docker 이미지 정리
echo "### Pruning unused docker images..."
docker image prune -f

echo "### Deployment finished successfully!"
