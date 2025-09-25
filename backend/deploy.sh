#!/bin/bash
# 디버그 모드를 활성화하여 모든 실행 명령어를 출력합니다.
set -x
# 스크립트 실행 중 오류가 발생하면 즉시 중단하도록 설정합니다.
set -e

# GitHub Actions에서 전달받은 ECR 이미지 URI를 변수에 할당합니다.
ECR_IMAGE_URI=$1

# ECR_IMAGE_URI가 비어있는 경우 오류를 출력하고 스크립트를 종료합니다.
if [ -z "$ECR_IMAGE_URI" ]; then
  echo "Error: ECR Image URI not provided." >&2
  exit 1
fi

# Nginx 로그를 저장할 디렉토리를 생성하고 권한을 설정합니다.
echo "### Creating and setting permissions for log directory..."
mkdir -p log/nginx
chmod 777 log/nginx

# .env 파일 존재 여부를 확인합니다.
echo "### Verifying .env file..."
if [ ! -f .env ]; then
  echo ".env file does NOT exist!" >&2
  exit 1
fi

# AWS CLI가 설치되어 있는지 확인하고, 없으면 설치합니다.
echo "### Checking for AWS CLI..."
if ! command -v aws &> /dev/null; then
    echo "AWS CLI not found, installing..."
    # yum 또는 apt-get을 사용하여 unzip 설치 시도
    sudo yum install -y unzip || (sudo apt-get update -y && sudo apt-get install -y unzip)
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip -q awscliv2.zip
    sudo ./aws/install
    rm -rf awscliv2.zip aws
fi

# ECR 이미지 URI에서 리전과 레지스트리 주소를 추출합니다.
AWS_REGION=$(echo $ECR_IMAGE_URI | cut -d'.' -f4)
ECR_REGISTRY=$(echo $ECR_IMAGE_URI | cut -d'/' -f1)

# AWS ECR에 로그인합니다.
echo "### Logging in to Amazon ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# docker-compose.yml에서 사용할 수 있도록 ECR_IMAGE_URI 변수를 export합니다.
export ECR_IMAGE_URI

echo "### Pulling the latest api image from ECR..."
# docker-compose.yml에 명시된 `api` 서비스의 이미지를 가져옵니다.
docker-compose -f docker-compose.yml -p backend pull api

# 충돌을 방지하기 위해 기존 컨테이너를 삭제합니다.
echo "### Removing conflicting containers to ensure a clean start..."
docker rm -f my-api my-nginx my-log-processor || true

echo "### Restarting services with the new image..."
# `docker-compose.override.yml` 없이 `docker-compose.yml`만 사용합니다.
# --build 플래그를 추가하여 log-processor 이미지를 항상 새로 빌드하도록 강제합니다.
docker-compose -f docker-compose.yml -p backend up -d --build --no-deps nginx api log-processor

# api 컨테이너가 완전히 시작될 때까지 잠시 대기합니다.
echo "### Waiting for services to be ready..."
sleep 10

# 사용하지 않는 Docker 이미지를 정리하여 디스크 공간을 확보합니다.
echo "### Cleaning up old images..."
docker image prune -af || true

echo "### Deployment finished successfully with image: $ECR_IMAGE_URI"