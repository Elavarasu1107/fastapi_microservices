from datetime import datetime, timedelta
from settings import settings
from fastapi import Security, Request, HTTPException
from fastapi.security import APIKeyHeader
from user.app.models import User
import jwt
from user.app import password

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

api_header = APIKeyHeader(name='Authorization', auto_error=False)


def access_token(payload: dict):
    payload['exp'] = datetime.utcnow() + payload['exp'] if 'exp' in payload.keys() else \
        datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, settings.jwt_key, settings.algorithm)


def refresh_token(payload: dict):
    payload['exp'] = datetime.utcnow() + payload['exp'] if 'exp' in payload.keys() else \
        datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, settings.jwt_key, settings.algorithm)


def decode_token(token: str):
    try:
        return jwt.decode(token, settings.jwt_key, algorithms=[settings.algorithm])
    except jwt.PyJWTError as e:
        raise e


def authenticate(data):
    user = User.objects.get_or_none(username=data['username'])
    if user and password.check_password(user, data['password']):
        return user
    return None


def api_key_authenticate(api_key: str):
    try:
        payload = decode_token(api_key)
        user = User.objects.get_or_none(id=payload.get('user'))
    except Exception as ex:
        raise ex
    return user.to_dict()
