from functools import wraps
from flask import request, jsonify, current_app
import jwt
from app.models import User

def token_required(f):
    """JWT 토큰을 검증하는 데코레이터"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # 1. HTTP 요청 헤더에서 'Authorization' 키 확인
        if 'Authorization' in request.headers:
            # 'Bearer <token>' 형식으로 전달된 토큰 파싱
            auth_header = request.headers['Authorization'].split(' ')
            if len(auth_header) == 2 and auth_header[0].lower() == 'bearer':
                token = auth_header[1]
            else:
                return jsonify({'message': '잘못된 형식의 토큰입니다. \'Bearer <token>\' 형식으로 전달해야 합니다.'}), 401
 
        if not token:
            return jsonify({'message': '인증 토큰이 없습니다.'}), 401

        try:
            # 2. 토큰 디코딩
            secret_key = current_app.config['JWT_SECRET_KEY']
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # 3. 토큰 페이로드에서 사용자 ID를 가져와 DB에서 사용자 조회
            current_user = User.query.get(payload['userId'])
            if current_user is None:
                return jsonify({'message': '유효하지 않은 토큰입니다.'}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({'message': '토큰이 만료되었습니다.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '유효하지 않은 토큰입니다.'}), 401

        # 4. 원래 호출하려던 함수(API 로직)를 실행. current_user 객체를 전달.
        return f(current_user, *args, **kwargs)
    return decorated