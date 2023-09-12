from fastapi import APIRouter, Request, Response, status, Depends, Security
from fastapi.security import APIKeyHeader
from . import schemas, dependencies
from settings import logger
from fastapi.responses import JSONResponse
from core.utils import APIResponse
from user.app import auth
from core.graph_db import Note

router = APIRouter(dependencies=[Security(APIKeyHeader(name='Authorization', auto_error=False)),
                                 Depends(auth.check_user)])


@router.post('/create/', status_code=status.HTTP_201_CREATED, response_class=JSONResponse,
             responses={201: {'model': APIResponse}})
def create_note(request: Request, data: schemas.NoteSchema, response: Response):
    try:
        data = data.dict()
        note = Note(**data).save()
        note.user.connect(request.state.user)
        note = schemas.NoteResponse.from_orm(note)
        reminder = data.get('reminder')
        if reminder:
            payload = {'message': note.description, 'subject': note.title, 'recipient': request.state.user.email}
            dependencies.send_reminder(payload, reminder, f'{note.id}-{note.title}')
        return {'message': 'Note created', 'status': 201, 'data': note}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex)}


@router.get("/get/", status_code=status.HTTP_200_OK, response_class=JSONResponse,
            responses={200: {'model': APIResponse}})
def get_user_notes(request: Request, response: Response):
    try:
        notes = request.state.user.notes.all() + request.state.user.collab_notes.all()
        notes = [schemas.NoteResponse.from_orm(i) for i in notes]
        return {'message': 'Notes retrieved', 'status': 200, 'data': notes}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex)}


@router.get("/retrieve/", status_code=status.HTTP_200_OK, response_class=JSONResponse,
            responses={200: {'model': APIResponse}})
def retrieve(request: Request, response: Response, note_id: str):
    try:
        note = Note.nodes.get_or_none(id=note_id, user=request.state.user.id)
        if not note:
            raise Exception('Note not found')
        note = schemas.NoteResponse.from_orm(note)
        return {'message': 'Notes retrieved', 'status': 200, 'data': note}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex)}


@router.put("/update/", status_code=status.HTTP_200_OK, response_class=JSONResponse,
            responses={200: {'model': APIResponse}})
def update_note(request: Request, response: Response, note_id: str, data: schemas.NoteSchema):
    try:
        data = data.dict()
        note = dependencies.note_availability(note_id=note_id, user=request.state.user)
        [setattr(note, x, y) for x, y in data.items()]
        note.save()
        note = schemas.NoteResponse.from_orm(note)
        return {'message': 'Note updated', 'status': 200, 'data': note}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex)}


@router.delete("/delete/", status_code=status.HTTP_200_OK, response_class=JSONResponse,
               responses={200: {'model': APIResponse}})
def delete_note(request: Request, response: Response, note_id: str):
    try:
        note = Note.nodes.get_or_none(id=note_id)
        if not note or not note.user.is_connected(request.state.user):
            raise Exception('Note not found')
        note.delete()
        return {'message': 'Note deleted', 'status': 200, 'data': {}}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex)}


@router.post('/addCollaborator/', status_code=status.HTTP_200_OK,
             responses={200: {'model': APIResponse}})
def add_collaborator(request: Request, response: Response, data: schemas.Collaborator):
    try:
        note = Note.nodes.get_or_none(id=data.note_id)
        if not note or not note.user.is_connected(request.state.user):
            raise Exception('Note not found')
        collaborators = note.collaborator.all()
        for user in data.user_id:
            user_data = auth.fetch_user(user)
            if not user_data:
                raise Exception(f'User {user} not found')
            if user_data not in collaborators:
                note.collaborator.connect(user_data, {'grant_access': data.grant_access})
        return {'message': 'Collaborator added', 'status': 200, 'data': {}}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex)}


@router.delete('/deleteCollaborator/', status_code=status.HTTP_200_OK,
               responses={200: {'model': APIResponse}})
def delete_collaborator(request: Request, response: Response, data: schemas.Collaborator):
    try:
        note = Note.nodes.get_or_none(id=data.note_id)
        if not note or not note.user.is_connected(request.state.user):
            raise Exception('Note not found')
        for user in data.user_id:
            user_data = auth.fetch_user(user)
            if not user_data:
                raise Exception(f'User {user} not found')
            note.collaborator.disconnect(user_data)
        return {'message': 'Collaborator deleted', 'status': 200, 'data': {}}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex)}


@router.post('/addLabelWithNote/', status_code=status.HTTP_200_OK, response_class=JSONResponse,
             responses={200: {'model': APIResponse}})
def add_label_with_note(request: Request, response: Response, data: schemas.LabelAssociate):
    try:
        note = dependencies.note_availability(note_id=data.note_id, user=request.state.user)
        for label in data.labels:
            label_data = dependencies.fetch_label(label_id=label, user=request.state.user)
            if not label_data:
                raise Exception(f'Label {label} not found')
            note.labels.connect(label_data)
        return {'message': 'Label associated with note', 'status': 200, 'data': {}}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex), 'status': response.status_code, 'data': {}}


@router.delete('/deleteLabelFromNote/', status_code=status.HTTP_200_OK, response_class=JSONResponse,
               responses={200: {'model': APIResponse}})
def delete_label_from_note(request: Request, response: Response, data: schemas.LabelAssociate):
    try:
        note = dependencies.note_availability(note_id=data.note_id, user=request.state.user)
        for label in data.labels:
            label_data = dependencies.fetch_label(label_id=label, user=request.state.user)
            if not label_data:
                raise Exception(f'Label {label} not found')
            note.labels.connect(label_data)
        return {'message': 'Label removed from note', 'status': 200, 'data': {}}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex), 'status': response.status_code, 'data': {}}
