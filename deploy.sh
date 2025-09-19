#!/bin/bash
# 스크립트 실행 중 오류가 발생하면 즉시 중단합니다.
set -e

# GitHub Actions에서 전달된 환경 변수를 사용합니다.
# GITHUB_REPOSITORY는 'CloudDx/hyeyeon'과 같은 형태입니다.
PROJECT_DIR="onpremise-webservice"

echo "### Cloning/Pulling repository..."
if [ ! -d "$PROJECT_DIR" ]; then
  # Public repository이므로 HTTPS로 clone합니다.
  git clone https://github.com/CloudDx/hyeyeon.git "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"
git pull origin main

# .env 파일 생성
echo "### Creating .env file..."
# GitHub Actions에서 Base64로 인코딩하여 전달한 ENV_FILE_CONTENT를
# 서버에서 디코딩하여 .env 파일을 올바르게 생성합니다.
echo "${ENV_FILE_CONTENT}" | base64 --decode > .env
# GitHub Actions에서 빌드한 최신 이미지를 받아옵니다.
echo "### Pulling the latest docker image..."
docker pull gpdus4605/onpremise-webservice:${GITHUB_SHA}
 
# docker-compose.yml을 직접 수정하는 대신, docker-compose.override.yml 파일을 생성하여
# api 서비스의 이미지를 동적으로 지정합니다. 이 방식이 더 안전하고 유연합니다.
echo "### Creating docker-compose.override.yml..."
cat <<EOF > docker-compose.override.yml
services:
  api:
    image: gpdus4605/onpremise-webservice:${GITHUB_SHA}
EOF

echo "### Restarting services with the new image..."
docker compose up -d --remove-orphans

# DB 마이그레이션
echo "### Running database migrations..."
docker compose exec api flask db upgrade

echo "### Deployment finished successfully!"
