#!/bin/bash
# 최초 서버 설정 스크립트 (setup.sh)
set -e
 
# 1. 환경변수 설정 (필요시 .env 파일 등에서 로드)
export DOMAIN_NAME="www.gpdus4605.site"
export CERTBOT_EMAIL="gpdus4605@naver.com"
export GITHUB_REPO_URL="https://github.com/CloudDx/hyeyeon.git"
# ... 기타 필요한 변수들 (스크립트에서 사용한다면 여기에 추가)

PROJECT_DIR="onpremise-webservice"

# 2. Git 리포지토리 클론
echo "### Cloning repository..."
git clone "$GITHUB_REPO_URL" "$PROJECT_DIR"
cd "$PROJECT_DIR"

# 3. .env 파일 생성 (수동 또는 다른 방법으로 내용 채우기)
echo "### Please create .env file manually."
# 예: cp .env.example .env && nano .env
# 이 단계에서는 GitHub Secret을 사용할 수 없으므로 수동으로 생성해야 합니다.
read -p "Press [Enter] key after creating .env file..."

# 4. SSL 인증서 발급을 위한 준비
echo "### Issuing SSL certificate for the first time..."
# HTTPS 설정이 없는 임시 Nginx 설정 파일을 사용합니다.
cp nginx/nginx.conf.pre-ssl nginx/default.conf

# 5. 임시 Nginx 실행
docker compose up -d nginx

# 6. Certbot으로 인증서 발급
docker run --rm \
  -v "/etc/letsencrypt:/etc/letsencrypt" \
  -v "/var/www/certbot:/var/www/certbot" \
  certbot/certbot certonly --webroot -w /var/www/certbot --force-renewal \
  --email "${CERTBOT_EMAIL}" -d "${DOMAIN_NAME}" --agree-tos -n

# 7. 임시 Nginx 종료 및 설정 파일 원복
docker compose down
git checkout HEAD -- nginx/default.conf

# 8. 모든 서비스 시작 (Certbot 갱신 포함)
echo "### Starting all services..."
docker compose up -d

echo "### Initial setup finished successfully!"
