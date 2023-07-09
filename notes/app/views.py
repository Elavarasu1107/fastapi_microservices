from fastapi import APIRouter, Request, Response, status, Depends, Security, HTTPException
from fastapi.security import APIKeyHeader
from . import schemas, dependencies
from .models import Notes, Collaborator
from settings import logger, settings
from fastapi.responses import JSONResponse

router = APIRouter(dependencies=[Security(APIKeyHeader(name='Authorization', auto_error=False)),
                                 Depends(dependencies.check_user)])


@router.post('/create/', status_code=status.HTTP_201_CREATED, response_class=JSONResponse)
def create_note(request: Request, data: schemas.NoteSchema, response: Response):
    try:
        data = data.dict()
        data.update({'user_id': request.state.user.get('id')})
        note = Notes.objects.create(**data)
        return {'message': 'Note created', 'status': 201, 'data': note.to_dict()}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex)}


@router.get("/get/", status_code=status.HTTP_200_OK, response_class=JSONResponse)
def get_note(request: Request, response: Response):
    try:
        note_list = list(map(lambda x: x.to_dict(), Notes.objects.filter(user_id=request.state.user.get('id'))))
        collab_notes = list(map(lambda x: Notes.objects.get(id=x.note_id).to_dict(),
                                Collaborator.objects.filter(user_id=request.state.user.get('id'))))
        note_list.extend(collab_notes)
        return {'message': 'Notes retrieved', 'status': 200, 'data': note_list}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex)}


@router.put("/update/", status_code=status.HTTP_200_OK, response_class=JSONResponse)
def update_note(request: Request, response: Response, note_id: int, data: schemas.NoteSchema):
    try:
        note = Notes.objects.get(id=note_id, user_id=request.state.user.get('id'))
        data = data.dict()
        data.update({'id': note_id, 'user_id': request.state.user.get('id')})
        note.objects.update(**data)
        return {'message': 'Note updated', 'status': 200, 'data': note.to_dict()}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex)}


@router.delete("/delete/", status_code=status.HTTP_200_OK, response_class=JSONResponse)
def delete_note(request: Request, response: Response, note_id: int):
    try:
        Notes.objects.delete(id=note_id, user_id=request.state.user.get('id'))
        return {'message': 'Note deleted', 'status': 200, 'data': {}}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex)}


@router.post('/addCollaborator/', status_code=status.HTTP_200_OK)
def add_collaborator(request: Request, response: Response, data: schemas.Collaborator):
    try:
        note = Notes.objects.get(id=data.note_id, user_id=request.state.user.get('id'))
        collab_obj = []
        for user in data.user_id:
            user_data = dependencies.fetch_user(user)
            if not user_data:
                raise Exception(f'User {user} not found')
            collab_obj.append(Collaborator(note_id=note.id, user_id=user_data['id']))
        Collaborator.objects.bulk_create(collab_obj)
        return {'message': 'Collaborator added', 'status': 200, 'data': {}}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex)}


@router.delete('/deleteCollaborator/', status_code=status.HTTP_200_OK)
def delete_collaborator(request: Request, response: Response, data: schemas.Collaborator):
    try:
        note = Notes.objects.get(id=data.note_id, user_id=request.state.user.get('id'))
        collab_obj = []
        for user in data.user_id:
            user_data = dependencies.fetch_user(user)
            if not user_data:
                raise Exception(f'User {user} not found')
            collab_user = Collaborator.objects.get_or_none(note_id=note.id, user_id=user)
            if not collab_user:
                raise Exception(f'Note {data.note_id} is not collaborated with user {user}')
            collab_obj.append(collab_user)
        [Collaborator.objects.delete(id=x.id) for x in collab_obj]
        return {'message': 'Collaborator deleted', 'status': 200, 'data': {}}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex)}
