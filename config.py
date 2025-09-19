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

    def __init__(self):
        """인스턴스가 생성될 때 환경 변수를 읽어 URI를 설정합니다."""
        super().__init__()
        postgres_user = os.environ.get('POSTGRES_USER')
        postgres_password = os.environ.get('POSTGRES_PASSWORD')
        postgres_db = os.environ.get('POSTGRES_DB')
        db_host = 'db'  # docker-compose 서비스 이름
        db_port = '5432' # 컨테이너 내부 포트

        if not all([postgres_user, postgres_password, postgres_db]):
            raise ValueError("Database connection environment variables are not fully set.")

        self.SQLALCHEMY_DATABASE_URI = f"postgresql://{postgres_user}:{postgres_password}@{db_host}:{db_port}/{postgres_db}"

# 사용할 설정을 지정합니다. (예: 'development', 'production')
# 이 값도 환경 변수로 관리하여 실행 환경에 따라 설정을 바꿀 수 있습니다.
config_by_name = dict(
    dev=DevelopmentConfig,
    prod=ProductionConfig
)