# 이 파일은 게시글 관련 API 엔드포인트(CRUD)를 정의하는 곳입니다.
from flask import Blueprint, request, jsonify
from app.models import Post
from app import db
from app.utils.decorators import token_required

bp = Blueprint('post_routes', __name__)

@bp.route('', methods=['POST'])
@token_required
def create_post(current_user):
    """게시글 작성 API"""
    data = request.get_json()

    title = data.get('title')
    content = data.get('content')

    if not all([title, content]):
        return jsonify({"message": "제목과 내용을 모두 입력해주세요."}), 400

    new_post = Post(title=title, content=content, user_id=current_user.id)
    db.session.add(new_post)
    db.session.commit()

    return jsonify({
        "postId": new_post.id,
        "title": new_post.title,
        "content": new_post.content,
        "author": current_user.username,
        "createdAt": new_post.created_at.isoformat()
    }), 201

@bp.route('', methods=['GET'])
def get_posts():
    """전체 게시글 목록 조회 API"""
    # 모든 게시글을 created_at 기준으로 내림차순(최신순)으로 정렬하여 가져옵니다.
    posts = Post.query.order_by(Post.created_at.desc()).all()

    # 각 post 객체를 JSON 형식에 맞게 가공합니다.
    results = [
        {
            "postId": post.id,
            "title": post.title,
            # 'author'는 relationship으로 연결된 User 객체이므로, post.author.username으로 접근합니다.
            "author": post.author.username,
            "createdAt": post.created_at.isoformat()
        } for post in posts
    ]

    return jsonify(results), 200

@bp.route('/<int:post_id>', methods=['GET'])
def get_post_detail(post_id):
    """특정 게시글 상세 조회 API"""
    # post_id에 해당하는 게시글을 데이터베이스에서 찾습니다. 없으면 None을 반환합니다.
    post = Post.query.get(post_id)

    # 게시글이 존재하지 않는 경우, 404 Not Found 오류를 반환합니다.
    if post is None:
        return jsonify({"message": "게시글을 찾을 수 없습니다."}), 404

    return jsonify({
        "postId": post.id,
        "title": post.title,
        "content": post.content,
        "author": post.author.username,
        "createdAt": post.created_at.isoformat(),
        "updatedAt": post.updated_at.isoformat()
    }), 200

@bp.route('/<int:post_id>', methods=['PUT'])
@token_required
def update_post(current_user, post_id):
    """특정 게시글 수정 API"""
    # 1. 수정할 게시글을 DB에서 조회
    post = Post.query.get(post_id)

    if post is None:
        return jsonify({"message": "게시글을 찾을 수 없습니다."}), 404

    # 2. 게시글 작성자와 현재 로그인한 사용자가 동일한지 확인
    if post.author.id != current_user.id:
        return jsonify({"message": "게시글을 수정할 권한이 없습니다."}), 403

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not all([title, content]):
        return jsonify({"message": "제목과 내용을 모두 입력해주세요."}), 400

    # 3. 게시글 정보 업데이트 및 DB 저장
    post.title = title
    post.content = content
    db.session.commit()

    return jsonify({"message": "게시글이 성공적으로 수정되었습니다."}), 200

@bp.route('/<int:post_id>', methods=['DELETE'])
@token_required
def delete_post(current_user, post_id):
    """특정 게시글 삭제 API"""
    # 1. 삭제할 게시글을 DB에서 조회
    post = Post.query.get(post_id)

    if post is None:
        return jsonify({"message": "게시글을 찾을 수 없습니다."}), 404

    # 2. 게시글 작성자와 현재 로그인한 사용자가 동일한지 확인
    if post.author.id != current_user.id:
        return jsonify({"message": "게시글을 삭제할 권한이 없습니다."}), 403

    # 3. 게시글 DB에서 삭제
    db.session.delete(post)
    db.session.commit()

    # 204 No Content 응답은 body가 없어야 하므로, 빈 응답을 반환합니다.
    return '', 204