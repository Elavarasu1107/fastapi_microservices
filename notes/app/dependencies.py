from fastapi import HTTPException, Request
from settings import settings
import requests
from core.rmq_producer import Producer
from user.app import auth


def check_user(request: Request):
    try:
        if not request.headers.get('authorization'):
            raise HTTPException(detail='Jwt token required', status_code=401)
        payload = auth.decode_token(token=request.headers.get('authorization'), aud=auth.Audience.login.value)
        producer = Producer()
        producer.publish('cb_check_user', payload=payload)
        request.state.user = producer.response
    except Exception as ex:
        raise HTTPException(detail=str(ex), status_code=400)


def fetch_user(user_id: int):
    producer = Producer()
    producer.publish('cb_check_user', payload={'user': user_id})
    return producer.response


def fetch_label(note_id, token):
    try:
        res = requests.get(f'{settings.base_url}:{settings.label_port}/label/retrieve/',
                           params={'note_id': note_id}, headers={'Authorization': token})
    except requests.ConnectionError:
        return '404. Unable to communicate with label services'
    if res.status_code >= 400:
        return None
    return res.json().get('data')
