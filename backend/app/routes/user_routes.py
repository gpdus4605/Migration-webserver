# 이 파일은 사용자 관련 API 엔드포인트(회원가입, 로그인 등)를 정의하는 곳입니다.

from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db
import re
import jwt
import datetime

# '/api/users' 로 시작하는 URL들을 처리할 Blueprint 객체를 생성합니다.
bp = Blueprint('user_routes', __name__)

@bp.route('/signup', methods=['POST'])
def signup():
    """회원가입 API"""
    data = request.get_json()

    # 1. 요청 데이터 유효성 검사
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not all([email, username, password]):
        return jsonify({"message": "모든 필드를 입력해주세요."}), 400

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"message": "유효한 이메일 형식이 아닙니다."}), 400
    
    if len(username) < 3:
        return jsonify({"message": "닉네임은 3자 이상이어야 합니다."}), 400

    if len(password) < 8:
        return jsonify({"message": "비밀번호는 8자 이상이어야 합니다."}), 400

    # 2. 이메일, 닉네임 중복 확인
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "이미 사용중인 이메일입니다."}), 409
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "이미 사용중인 닉네임입니다."}), 409

    # 3. 비밀번호 암호화 및 사용자 생성
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(email=email, username=username, password=hashed_password)

    # 4. DB에 저장
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"userId": new_user.id, "email": new_user.email, "username": new_user.username}), 201

@bp.route('/login', methods=['POST'])
def login():
    """로그인 API"""
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({"message": "이메일과 비밀번호를 모두 입력해주세요."}), 400

    # 1. 이메일로 사용자 조회
    user = User.query.filter_by(email=email).first()

    # 2. 사용자가 존재하고 비밀번호가 일치하는지 확인
    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "이메일 또는 비밀번호가 올바르지 않습니다."}), 401

    # 3. JWT Access Token 생성
    payload = {
        'userId': user.id,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1) # 토큰 만료 시간 (1시간)
    }
    secret_key = current_app.config['JWT_SECRET_KEY']
    token = jwt.encode(payload, secret_key, algorithm='HS256')

    return jsonify({
        "accessToken": token,
        "userId": user.id,
        "username": user.username
    }), 200
