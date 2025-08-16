import time
from functools import wraps
from flask import request, jsonify
import jwt
from .settings import settings


def issue_token(payload: dict, ttl=60 * 60 * 24):
    payload = {**payload, 'exp': int(time.time()) + ttl}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'error': 'missing token'}), 401
        token = auth.split(' ', 1)[1]
        try:
            jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
        except Exception as e:
            return jsonify({'error': 'invalid token', 'detail': str(e)}), 401
        return fn(*args, **kwargs)

    return wrapper
