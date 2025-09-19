# --- 1. Base Image ---
# Python 3.12 버전을 기반으로 하는 공식 이미지를 사용합니다.
# 'slim' 버전은 운영 환경에 필요한 최소한의 패키지만 포함하여 이미지 크기를 줄여줍니다.
FROM python:3.12-slim

# --- 2. Set Working Directory ---
# 컨테이너 내에서 작업할 디렉토리를 설정합니다.
# 이 경로로 소스 코드가 복사되고, 명령어가 실행됩니다.
WORKDIR /usr/src/app

# --- 3. Install Dependencies ---
# 먼저 의존성 정의 파일만 복사합니다.
# (소스 코드가 변경되어도 이 부분이 바뀌지 않으면 Docker는 캐시를 사용하여 빌드 속도를 높입니다.)
COPY requirements.txt ./

# pip를 최신 버전으로 업그레이드하고, requirements.txt에 명시된 패키지들을 설치합니다.
# --no-cache-dir 옵션은 불필요한 캐시를 저장하지 않아 이미지 크기를 최적화합니다.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- 5. Copy Application Code ---
# 프로젝트의 모든 소스 코드를 컨테이너의 작업 디렉토리로 복사합니다.
COPY . .

# --- 6. Add Entrypoint Script ---
# entrypoint.sh 스크립트를 복사하고 실행 권한을 부여합니다.
COPY entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# --- 6. Expose Port ---
# 컨테이너가 외부와 통신할 포트를 지정합니다. Flask 기본 포트인 5000번을 엽니다.
EXPOSE 5000

# --- 7. Set Entrypoint ---
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

# --- 7. Run Application ---
# 컨테이너가 시작될 때 실행할 명령어를 정의합니다.
# Gunicorn WSGI 서버를 사용하여 애플리케이션을 실행합니다.
# 'run:app'은 run.py 파일 안에 있는 app 객체를 의미합니다.
# 0.0.0.0 호스트는 컨테이너 외부에서의 접속을 허용합니다.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]