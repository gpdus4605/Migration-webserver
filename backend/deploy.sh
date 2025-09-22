#!/bin/bash
# 이 스크립트의 모든 출력을 /tmp/deploy.log 파일에 기록합니다.
# 표준 출력(stdout)과 표준 에러(stderr)를 모두 리디렉션합니다.
exec > >(tee -a /tmp/deploy.log) 2>&1

# 스크립트 실행 중 오류가 발생하면 즉시 중단하도록 설정합니다.
# 이 설정은 exec 이후에 위치해야 합니다.
set -e

# GitHub Actions에서 전달된 환경 변수를 사용합니다.
# GITHUB_REPOSITORY는 'CloudDx/hyeyeon'과 같은 형태입니다.

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
# -p onpremise: 프로젝트 이름을 'onpremise'로 고정하여 항상 동일한 컨테이너 그룹을 관리하도록 합니다.
# --env-file ./.env: 현재 디렉터리의 .env 파일을 환경 변수 파일로 명시적으로 지정합니다.
# 이렇게 하면 docker-compose가 환경 변수를 확실하게 읽어들여 경고를 없애고,
# 기존에 실행 중인 컨테이너를 '재시작(recreate)' 또는 '업데이트'하여 이름 충돌 없이 배포를 완료합니다.
# nginx와 api 서비스만 대상으로 지정하여 db와 certbot 컨테이너와의 충돌을 원천적으로 방지합니다.
# -f 옵션으로 docker-compose.yml 파일의 절대 경로를 명시하여 실행 컨텍스트 문제를 완전히 해결합니다.
# --build 옵션을 제거하여 서버에서 불필요한 빌드를 시도하지 않도록 합니다.
docker-compose -f /home/ubuntu/onpremise-webservice/backend/docker-compose.yml -p onpremise up -d --no-deps nginx api

# api 컨테이너가 완전히 시작될 때까지 잠시 대기합니다.
# 애플리케이션의 시작 시간에 따라 5~10초 정도의 대기 시간을 주는 것이 안정적입니다.
echo "### Waiting for services to be ready..."
sleep 10

# 사용하지 않는 Docker 이미지를 정리하여 디스크 공간을 확보합니다.
echo "### Cleaning up unused docker images..."
# || true를 추가하여, 삭제할 이미지가 없어 명령어가 실패하더라도 전체 스크립트가 중단되지 않도록 합니다.
docker image prune -af || true

echo "### Deployment finished successfully!"
