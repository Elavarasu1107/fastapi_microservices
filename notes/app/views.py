from bson import ObjectId
from fastapi import APIRouter, Request, Response, status, Depends, Security, HTTPException
from fastapi.security import APIKeyHeader
from . import schemas, dependencies
from settings import logger, settings
from fastapi.responses import JSONResponse
from core.utils import APIResponse
from core.monogodb import Notes

router = APIRouter(dependencies=[Security(APIKeyHeader(name='Authorization', auto_error=False)),
                                 Depends(dependencies.check_user)])


@router.post('/create/', status_code=status.HTTP_201_CREATED, response_class=JSONResponse,
             responses={201: {'model': APIResponse}})
def create_note(request: Request, data: schemas.NoteSchema, response: Response):
    try:
        data = data.dict()
        data.update({'user': ObjectId(request.state.user.get('_id'))})
        note = Notes.insert_one(data)
        note = Notes.find_one({'_id': ObjectId(note.inserted_id)})
        note = schemas.NoteResponse(**note)
        return {'message': 'Note created', 'status': 201, 'data': note}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex)}


@router.get("/get/", status_code=status.HTTP_200_OK, response_class=JSONResponse,
            responses={200: {'model': APIResponse}})
def get_user_notes(request: Request, response: Response):
    try:
        notes = list(Notes.find({'user': ObjectId(request.state.user.get('_id'))}))
        collab_notes = list(Notes.find({f'collaborators.{request.state.user.get("_id")}': {'$exists': True}}))
        notes.extend(collab_notes)
        notes = [schemas.NoteResponse(**i) for i in notes]
        return {'message': 'Notes retrieved', 'status': 200, 'data': notes}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex)}


@router.get("/retrieve/", status_code=status.HTTP_200_OK, response_class=JSONResponse,
            responses={200: {'model': APIResponse}})
def retrieve(request: Request, response: Response, note_id: str):
    try:
        note = Notes.find_one({'_id': ObjectId(note_id)})
        if not note:
            raise Exception('Note not found')
        note = schemas.NoteResponse(**note)
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
        note = Notes.find_one_and_update({'_id': ObjectId(note_id), 'user': ObjectId(request.state.user.get('_id'))},
                                         {'$set': data})
        if not note:
            note = Notes.find_one({'_id': ObjectId(note_id),
                                   f'collaborators.{request.state.user.get("_id")}': {'$exists': True}})
        if not note:
            raise Exception('Note not found')
        if not note.get('collaborators').get(request.state.user.get("_id"))[1].get('grant_access'):
            raise Exception('Access denied to update this note')
        note = Notes.update_one(note, {'$set': data})
        note = Notes.find_one({'_id': ObjectId(note_id)})
        note = schemas.NoteResponse(**note)
        return {'message': 'Note updated', 'status': 200, 'data': note}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex)}


@router.delete("/delete/", status_code=status.HTTP_200_OK, response_class=JSONResponse,
               responses={200: {'model': APIResponse}})
def delete_note(request: Request, response: Response, note_id: str):
    try:
        note = Notes.find_one_and_delete({'_id': ObjectId(note_id), 'user': ObjectId(request.state.user.get('_id'))})
        if not note:
            raise Exception('Note not found')
        return {'message': 'Note deleted', 'status': 200, 'data': {}}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex)}


@router.post('/addCollaborator/', status_code=status.HTTP_200_OK,
             responses={200: {'model': APIResponse}})
def add_collaborator(request: Request, response: Response, data: schemas.Collaborator):
    try:
        note = Notes.find_one({'_id': ObjectId(data.note_id), 'user': ObjectId(request.state.user.get('_id'))})
        if not note:
            raise Exception('Note not found')
        collaborators = {}
        for user in data.user_id:
            user_data = dependencies.fetch_user(user)
            if not user_data:
                raise Exception(f'User {user} not found')
            collaborators.update({f'collaborators.{ObjectId(user_data["_id"])}': [{'$ref': 'user',
                                                                                   '$id': ObjectId(user_data["_id"]),
                                                                                   '$db': 'fundoo_microservices'},
                                                                                  {'grant_access': data.grant_access}]})
        note = Notes.find_one_and_update(note, {'$set': collaborators})
        return {'message': 'Collaborator added', 'status': 200, 'data': {}}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex)}


@router.delete('/deleteCollaborator/', status_code=status.HTTP_200_OK,
               responses={200: {'model': APIResponse}})
def delete_collaborator(request: Request, response: Response, data: schemas.Collaborator):
    try:
        note = Notes.find_one({'_id': ObjectId(data.note_id), 'user': ObjectId(request.state.user.get('_id'))})
        if not note:
            raise Exception('Note not found')
        collaborators = {}
        for user in data.user_id:
            user_data = dependencies.fetch_user(user)
            if not user_data:
                raise Exception(f'User {user} not found')
            collaborators.update({f'collaborators.{ObjectId(user_data["_id"])}': ""})
        Notes.update_one(note, {'$unset': collaborators})
        return {'message': 'Collaborator deleted', 'status': 200, 'data': {}}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex)}
