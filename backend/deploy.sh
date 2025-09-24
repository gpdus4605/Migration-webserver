#!/bin/bash
# 디버그 모드를 활성화하여 모든 실행 명령어를 출력합니다.
set -x
# 스크립트 실행 중 오류가 발생하면 즉시 중단하도록 설정합니다.
set -e

# Nginx 로그를 저장할 디렉토리를 생성하고 권한을 설정합니다.
echo "### Creating and setting permissions for log directory..."
mkdir -p log/nginx
chmod 777 log/nginx


# GITHUB_SHA는 GitHub Actions에서 환경 변수로 전달됩니다.
echo "### Using GITHUB_SHA: ${GITHUB_SHA}"

echo "### Verifying .env file..."
if [ -f .env ]; then
  echo ".env file exists."
  cat .env
else
  echo ".env file does NOT exist! It should have been copied via scp." >&2
  exit 1
fi

# GitHub Actions에서 빌드한 최신 이미지를 받아옵니다.
echo "### Pulling the latest docker images..."
docker pull gpdus4605/onpremise-webservice:${GITHUB_SHA}

# docker-compose.override.yml 파일을 생성하여 api 서비스의 이미지를 동적으로 지정합니다.
echo "### Creating docker-compose.override.yml..."
cat <<EOF > docker-compose.override.yml
services:
  api:
    image: gpdus4605/onpremise-webservice:${GITHUB_SHA}
EOF

echo "### Removing conflicting containers to ensure a clean start..."
docker rm -f my-api my-nginx || true

echo "### Restarting services with the new image..."
# -f 옵션으로 docker-compose.yml과 docker-compose.override.yml을 모두 지정합니다.
docker-compose -f docker-compose.yml -f docker-compose.override.yml -p backend up -d --no-deps nginx api

# api 컨테이너가 완전히 시작될 때까지 잠시 대기합니다.
echo "### Waiting for services to be ready..."
sleep 10

# 사용하지 않는 Docker 이미지를 정리하여 디스크 공간을 확보합니다.
echo "### Cleaning up old images..."
docker image prune -af || true

echo "### Deployment finished successfully!"