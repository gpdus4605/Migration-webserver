#!/bin/bash
# 이 스크립트의 모든 출력을 /tmp/deploy.log 파일에 기록합니다.
# 표준 출력(stdout)과 표준 에러(stderr)를 모두 리디렉션합니다.
exec > >(tee -a /tmp/deploy.log) 2>&1

# 스크립트 실행 중 오류가 발생하면 즉시 중단하도록 설정합니다.
# 이 설정은 exec 이후에 위치해야 합니다.
set -e

# GitHub Actions에서 전달된 환경 변수를 사용합니다.
# GITHUB_REPOSITORY는 'CloudDx/hyeyeon'과 같은 형태입니다.
HOME_DIR="/home/ubuntu" # 외부 변수 의존성을 제거하고 절대 경로를 명시합니다.
PROJECT_DIR="onpremise-webservice"
PROJECT_PATH="${HOME_DIR}/${PROJECT_DIR}" # 최종 경로는 /home/ubuntu/onpremise-webservice

echo "### Cloning/Pulling repository..."
if [ ! -d "$PROJECT_PATH" ]; then
  # Public repository이므로 HTTPS로 clone합니다.
  # git clone 자체가 HOME 변수를 참조하려는 문제를 피하기 위해,
  # 상위 디렉터리로 먼저 이동한 후 clone을 실행합니다.
  cd "$HOME_DIR"
  git clone https://github.com/CloudDx/hyeyeon.git "$PROJECT_PATH"
  cd "$PROJECT_PATH"
else
  cd "$PROJECT_PATH"
  git pull origin main
fi

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

# api 컨테이너가 완전히 시작될 때까지 잠시 대기합니다.
# 애플리케이션의 시작 시간에 따라 5~10초 정도의 대기 시간을 주는 것이 안정적입니다.
echo "### Waiting for services to be ready..."
sleep 10

# DB 마이그레이션
echo "### Running database migrations..."
docker compose exec api flask db upgrade

# 사용하지 않는 Docker 이미지를 정리하여 디스크 공간을 확보합니다.
echo "### Cleaning up unused docker images..."
docker image prune -af

echo "### Deployment finished successfully!"
