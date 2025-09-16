# 이 파일은 데이터베이스 테이블에 매핑될 SQLAlchemy 모델 클래스를 정의하는 곳입니다.
# 예를 들어, User 모델과 Post 모델이 여기에 위치하게 됩니다.

from . import db
from sqlalchemy.sql import func

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # User와 Post 모델 간의 관계 설정
    # 'posts'는 User 객체에서 자신의 모든 Post 객체에 접근하기 위한 속성입니다.
    # back_populates는 Post 모델의 'author' 속성과 연결됨을 의미합니다.
    posts = db.relationship('Post', back_populates='author')

    def __repr__(self):
        return f'<User {self.username}>'

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Post와 User 모델 간의 관계 설정
    # 'author'는 Post 객체에서 작성자 User 객체에 접근하기 위한 속성입니다.
    author = db.relationship('User', back_populates='posts')

    def __repr__(self):
        return f'<Post {self.title}>'

