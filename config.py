import os

class Config:
    """기본 설정"""
    # JWT 시크릿 키는 보안상 매우 중요하므로, 환경 변수에서 불러오는 것이 가장 좋습니다.
    # os.environ.get()을 사용하면 해당 환경 변수가 없을 때 None을 반환합니다.
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default-super-secret-key-for-dev')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True
    # 데이터베이스 연결 정보도 환경 변수로 관리하는 것이 좋습니다.
    # 예: postgresql://[사용자명]:[비밀번호]@[호스트]:[포트]/[데이터베이스명]
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost/mydatabase')

class ProductionConfig(Config):
    """운영 환경 설정"""
    DEBUG = False
    # 운영 환경에서는 반드시 환경 변수로부터 실제 DB 주소와 시크릿 키를 받아야 합니다.
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

    # 개별 환경 변수를 읽어 데이터베이스 URI를 동적으로 생성합니다.
    # 이 방식은 gunicorn, flask db 등 어떤 방식으로 실행되어도 동일하게 동작하여 가장 안정적입니다.
    POSTGRES_USER = os.environ.get('POSTGRES_USER')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
    POSTGRES_DB = os.environ.get('POSTGRES_DB')
    DB_HOST = 'db'  # docker-compose 서비스 이름
    DB_PORT = '5432' # 컨테이너 내부 포트

    # 모든 변수가 존재하는지 확인하고 URI를 조합합니다.
    if all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]):
        SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}"

# 사용할 설정을 지정합니다. (예: 'development', 'production')
# 이 값도 환경 변수로 관리하여 실행 환경에 따라 설정을 바꿀 수 있습니다.
config_by_name = dict(
    dev=DevelopmentConfig,
    prod=ProductionConfig
)