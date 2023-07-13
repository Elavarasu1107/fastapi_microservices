from fastapi import HTTPException, Request
from settings import settings
import requests


def check_user(request: Request):
    if not request.headers.get('authorization'):
        raise HTTPException(detail='Jwt token required', status_code=401)
    res = requests.post(f'{settings.base_url}:{settings.user_port}/authenticate/',
                        json={'token': request.headers.get('authorization')})
    if res.status_code >= 400:
        raise HTTPException(detail=res.json()['message'], status_code=res.status_code)
    request.state.user = res.json()


def fetch_user(user_id: int):
    res = requests.post(f'{settings.base_url}:{settings.user_port}/retrieve/',
                        params={'user_id': user_id})
    if res.status_code >= 400:
        return None
    return res.json().get('data')


def fetch_label(note_id, token):
    try:
        res = requests.get(f'{settings.base_url}:{settings.label_port}/label/retrieve/',
                           params={'note_id': note_id}, headers={'Authorization': token})
    except requests.ConnectionError:
        return '404. Unable to communicate with label services'
    if res.status_code >= 400:
        return None
    return res.json().get('data')
