#!/bin/sh
# 컨테이너 시작 시 실행될 스크립트

# 스크립트 실행 중 오류가 발생하면 즉시 중단합니다.
set -e

echo "### Starting entrypoint script..."

echo "### Running database migrations..."
# python3 -m flask를 사용하여 경로 문제 없이 마이그레이션을 실행합니다.
python3 -m flask db upgrade

echo "### Starting Gunicorn server..."
# 모든 작업이 끝나면 원래의 CMD 명령(gunicorn)을 실행합니다.
exec "$@"