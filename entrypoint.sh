#!/bin/sh
# 컨테이너 시작 시 실행될 스크립트

# 스크립트 실행 중 오류가 발생하면 즉시 중단합니다.
set -e

echo "### Starting entrypoint script..."

# DATABASE_URL을 동적으로 생성합니다.
# 이 스크립트는 컨테이너 내부에서 실행되므로, .env 파일의 변수들을 사용할 수 있습니다.
export DATABASE_URL="postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@db:5432/$POSTGRES_DB"

echo "### Running database migrations..."
# python3 -m flask를 사용하여 경로 문제 없이 마이그레이션을 실행합니다.
python3 -m flask db upgrade

echo "### Starting Gunicorn server..."
# 모든 작업이 끝나면 원래의 CMD 명령(gunicorn)을 실행합니다.
exec "$@"