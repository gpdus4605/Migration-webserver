import os
import sys

# 현재 파일의 상위 디렉토리(프로젝트 루트)를 시스템 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

# Application Factory를 통해 Flask 앱 인스턴스를 생성합니다.
# create_app 내부에서 FLASK_ENV 환경 변수를 읽어 설정을 로드합니다. (기본값 'dev')
app = create_app()

if __name__ == '__main__':
    # Flask 내장 개발 서버를 실행합니다.
    # host='0.0.0.0'은 외부에서 이 서버에 접속할 수 있도록 합니다.
    # port=5001을 사용합니다.
    # debug=True로 설정하면 코드 변경 시 서버가 자동으로 재시작되고 디버거가 활성화됩니다.
    app.run(host='0.0.0.0', port=5001, debug=True)
