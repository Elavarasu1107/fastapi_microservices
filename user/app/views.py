from fastapi import APIRouter, status, Request, Response, HTTPException
from . import schemas, auth
from core.utils import APIResponse
from core.tasks import send_mail
from core.monogodb import User
from settings import logger
from core.graph_db import User

router = APIRouter()


@router.post('/register/', status_code=status.HTTP_201_CREATED, responses={201: {'model': APIResponse}})
def register_user(request: Request, response: Response, data: schemas.RegisterValidation):
    try:
        user = User(**data.dict()).save()
        user = schemas.UserResponse.from_orm(user)
        message = f'{request.base_url}verify?token={auth.access_token({"user": user.id},aud=auth.Audience.register.value)}'
        send_mail.delay(payload={'recipient': user.email, 'message': message, 'subject': 'User registration'})
        return {'message': 'User registered', 'status': 201, 'data': user}
    except Exception as ex:
        response.status_code = status.HTTP_400_BAD_REQUEST
        logger.exception(ex)
        return {'message': ex.args[0], 'status': 400, 'data': {}}


@router.post('/login/', status_code=status.HTTP_200_OK, responses={200: {'model': APIResponse}})
def login_user(request: Request, response: Response, data: schemas.Login):
    user = auth.authenticate(data=data.dict())
    if not user and not user.is_verified:
        raise HTTPException(status_code=401, detail='Invalid Credentials')
    return {
        'access': auth.access_token({'user': user.id}, aud=auth.Audience.login.value),
        'refresh': auth.refresh_token({'user': user.id}, aud=auth.Audience.login.value)
    }


# @router.post('/authenticate/', status_code=status.HTTP_200_OK, include_in_schema=False)
# def authenticate_user(token: schemas.Token, response: Response):
#     try:
#         user = auth.api_key_authenticate(token.token, auth.Audience.login.value)
#         # if not user:
#         #     return {}
#         return user
#     except Exception as ex:
#         response.status_code = status.HTTP_401_UNAUTHORIZED
#         return {'message': str(ex)}


@router.post('/retrieve/', status_code=status.HTTP_200_OK, include_in_schema=False)
def retrieve_user(request: Request, response: Response, user_id: int = None):
    try:
        user = User.nodes.get(id=user_id)
        return {'message': 'User retrieved', 'status': 200, 'data': user}
    except Exception as ex:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'message': str(ex), 'status': 400, 'data': {}}


@router.get('/verify', status_code=status.HTTP_200_OK)
def verify_user(request: Request, response: Response, token: str = None):
    try:
        if not token:
            raise Exception('Token required to verify user registration')
        payload = auth.decode_token(token=token, aud=auth.Audience.register.value)
        user = auth.api_key_authenticate(payload, auth.Audience.register.value)
        if not user:
            raise Exception('User not found to verify')
        user.is_verified = True
        user.save()
        return {'message': 'User verified successfully', 'status': 200, 'data': {}}
    except Exception as ex:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'message': str(ex), 'status': 400, 'data': {}}
