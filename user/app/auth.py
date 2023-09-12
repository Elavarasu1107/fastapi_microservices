from datetime import datetime, timedelta
from settings import settings
from fastapi import Request, HTTPException
from fastapi.security import APIKeyHeader
import jwt
from user.app import password
from typing import List
import enum
from core.graph_db import User

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

api_header = APIKeyHeader(name='Authorization', auto_error=False)


class Audience(enum.Enum):
    login = 'login'
    register = 'register'
    default = 'default'


def access_token(payload: dict, aud: str = None):
    payload['exp'] = datetime.utcnow() + payload['exp'] if 'exp' in payload.keys() else \
        datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload['aud'] = aud if aud else Audience.default.value
    return jwt.encode(payload, settings.jwt_key, settings.algorithm)


def refresh_token(payload: dict, aud: str = None):
    payload['exp'] = datetime.utcnow() + payload['exp'] if 'exp' in payload.keys() else \
        datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    payload['aud'] = aud if aud else Audience.default.value
    return jwt.encode(payload, settings.jwt_key, settings.algorithm)


def decode_token(token: str, aud: List[str] = Audience.default.value):
    try:
        return jwt.decode(token, settings.jwt_key, algorithms=[settings.algorithm], audience=aud)
    except jwt.PyJWTError as e:
        raise e


def authenticate(data):
    user = User.nodes.get_or_none(username=data['username'])
    if user and password.check_password(user, data['password']):
        return user
    return None


def api_key_authenticate(payload: dict, aud: str):
    try:
        user = User.nodes.get(id=payload.get('user'))
    except Exception as ex:
        raise ex
    return user.json


def check_user(request: Request):
    try:
        if not request.headers.get('authorization'):
            raise Exception('Jwt token required')
        payload = decode_token(token=request.headers.get('authorization'), aud=[Audience.login.value])
        user = User.nodes.get(id=payload.get('user'))
        request.state.user = user
    except Exception as ex:
        raise HTTPException(detail=str(ex), status_code=400)


def fetch_user(user_id):
    user = User.nodes.get(id=user_id)
    return user

