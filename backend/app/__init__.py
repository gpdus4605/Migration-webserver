import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import config_by_name

# SQLAlchemy 객체를 초기화합니다.
# 아직 특정 앱에 연결되지 않은 상태입니다.
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """
    Application Factory 함수
    Flask 앱 인스턴스를 생성하고 설정합니다.
    """
    # frontend 폴더를 static_folder 및 template_folder로 지정
    # 이렇게 하면 Flask가 frontend 폴더에서 정적 파일(JS, CSS)과 템플릿을 찾습니다.
    # ../frontend 경로는 현재 파일(__init__.py) 위치에서 상위 디렉토리로 이동한 후
    # frontend 디렉토리를 가리킵니다.
    app = Flask(__name__,
                static_folder='../../frontend',
                template_folder='../../frontend')

    # --- 1. 설정 로드 ---
    # FLASK_ENV 환경 변수를 기반으로 설정을 로드합니다. (기본값: 'dev')
    config_name = os.getenv('FLASK_ENV', 'dev')
    config_object = config_by_name[config_name]
    app.config.from_object(config_object)

    # --- 2. 확장 초기화 ---
    # CORS를 앱에 적용합니다.
    # 특정 리소스(r"/api/*")에 대해 지정된 출처(origins)의 요청만 허용합니다.
    CORS(app, resources={
        r"/*": {
            "origins": [
                "http://localhost:8000",
                "https://www.gpdus4605.site",
                "https://d3rga30rmvg69e.cloudfront.net",
                "https://dhih6nud55l1x.cloudfront.net"
            ]
        }
    })

    # config_object의 모든 속성을 app.config에 명시적으로 다시 로드하여,
    # 동적으로 생성된 SQLALCHEMY_DATABASE_URI가 확실히 적용되도록 합니다.
    app.config.from_mapping(vars(config_object))

    # db 객체를 Flask 앱에 연결합니다.
    db.init_app(app)
    # Migrate 객체를 db와 app에 연결하여 'flask db' 명령어를 활성화합니다.
    migrate.init_app(app, db)

    # --- 3. 모델 및 블루프린트 등록 ---
    # Import models here to prevent circular dependencies.
    # JSON 응답에서 한글이 유니코드 이스케이프되지 않도록 설정합니다.
    app.json.ensure_ascii = False

    from . import models
    from .routes import user_routes, post_routes
    app.register_blueprint(user_routes.bp, url_prefix='/users')
    app.register_blueprint(post_routes.bp, url_prefix='/posts')

    # 루트 URL에 대한 라우트를 추가합니다.
    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    return app