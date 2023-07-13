from fastapi import APIRouter, status, Request, Response, HTTPException
from . import schemas, auth
from .models import User
from core.utils import APIResponse
from core.rmq_producer import Producer

router = APIRouter()


@router.post('/register/', status_code=status.HTTP_201_CREATED, responses={201: {'model': APIResponse}})
def register_user(request: Request, response: Response, data: schemas.RegisterValidation):
    try:
        data = data.dict()
        user = User.objects.create_user(**data)
        message = f'{request.base_url}verify?token={auth.access_token({"user": user.id}, aud=auth.Audience.register.value)}'
        Producer().publish(method='cb_mailer', payload={'recipient': user.email, 'message': message})
        return {'message': 'User registered', 'status': 201, 'data': user}
    except Exception as ex:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'message': ex.args[0], 'status': 400, 'data': {}}


@router.post('/login/', status_code=status.HTTP_200_OK, responses={200: {'model': APIResponse}})
def login_user(request: Request, response: Response, data: schemas.Login):
    data = data.dict()
    user = auth.authenticate(data)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid Credentials')
    return {
        'access': auth.access_token({'user': user.id}, aud=auth.Audience.login.value),
        'refresh': auth.refresh_token({'user': user.id}, aud=auth.Audience.login.value)
    }


@router.post('/authenticate/', status_code=status.HTTP_200_OK, include_in_schema=False)
def authenticate_user(token: schemas.Token, response: Response):
    try:
        user = auth.api_key_authenticate(token.token, auth.Audience.login.value)
        # if not user:
        #     return {}
        return user
    except Exception as ex:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {'message': str(ex)}


@router.post('/retrieve/', status_code=status.HTTP_200_OK, include_in_schema=False)
def retrieve_user(request: Request, response: Response, user_id: int = None):
    try:
        user = User.objects.get(id=user_id)
        return {'message': 'User retrieved', 'status': 200, 'data': user}
    except Exception as ex:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'message': str(ex), 'status': 400, 'data': {}}


@router.get('/verify', status_code=status.HTTP_200_OK)
def verify_user(request: Request, response: Response, token: str = None):
    try:
        if not token:
            raise Exception('Token required to verify user registration')
        user = auth.api_key_authenticate(token, auth.Audience.register.value)
        if not user:
            raise Exception('User not found to verify')
        user.is_verified = True
        user.save()
        return {'message': 'User verified successfully', 'status': 200, 'data': {}}
    except Exception as ex:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'message': str(ex), 'status': 400, 'data': {}}