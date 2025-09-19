import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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
    app = Flask(__name__)

    # --- 1. 설정 로드 ---
    # FLASK_ENV 환경 변수를 기반으로 설정을 로드합니다. (기본값: 'dev')
    config_name = os.getenv('FLASK_ENV', 'dev')
    config_object = config_by_name[config_name]
    app.config.from_object(config_object)

    # JSON 응답에서 한글이 유니코드 이스케이프되지 않도록 설정합니다.
    app.json.ensure_ascii = False

    # --- 2. 확장 초기화 ---
    # db 객체를 Flask 앱에 연결합니다.
    db.init_app(app)
    # Migrate 객체를 db와 app에 연결하여 'flask db' 명령어를 활성화합니다.
    migrate.init_app(app, db)

    # --- 3. 모델 및 블루프린트 등록 ---
    # Import models here to prevent circular dependencies.
    from . import models
    from .routes import user_routes, post_routes
    app.register_blueprint(user_routes.bp, url_prefix='/api/users')
    app.register_blueprint(post_routes.bp, url_prefix='/api/posts')

    # 루트 URL에 대한 라우트를 추가합니다.
    @app.route('/')
    def index():
        return render_template('index.html')

    return app