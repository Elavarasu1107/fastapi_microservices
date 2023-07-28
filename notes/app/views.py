from bson import ObjectId
from fastapi import APIRouter, Request, Response, status, Depends, Security
from fastapi.security import APIKeyHeader
from . import schemas, dependencies
from settings import logger
from fastapi.responses import JSONResponse
from core.utils import APIResponse
from core.monogodb import Notes
from user.app import auth

router = APIRouter(dependencies=[Security(APIKeyHeader(name='Authorization', auto_error=False)),
                                 Depends(auth.check_user)])


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
        notes = list(Notes.find({'$or': [
            {'user': ObjectId(request.state.user.get('_id'))},
            {f'collaborators.{request.state.user.get("_id")}': {'$exists': True}}
        ]}))
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
        note = dependencies.note_availability(note_id=note_id, user_id=request.state.user.get('_id'))
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
            user_data = auth.fetch_user(user)
            if not user_data:
                raise Exception(f'User {user} not found')
            collaborators.update({f'collaborators.{ObjectId(user_data["_id"])}': [{'$ref': 'user',
                                                                                   '$id': ObjectId(user_data["_id"]),
                                                                                   '$db': 'fundoo_microservices'},
                                                                                  {'grant_access': data.grant_access,
                                                                                   'username': user_data['username']}]})
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
            user_data = auth.fetch_user(user)
            if not user_data:
                raise Exception(f'User {user} not found')
            collaborators.update({f'collaborators.{ObjectId(user_data["_id"])}': ""})
        Notes.update_one(note, {'$unset': collaborators})
        return {'message': 'Collaborator deleted', 'status': 200, 'data': {}}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex)}


@router.post('/addLabelWithNote/', status_code=status.HTTP_200_OK, response_class=JSONResponse,
             responses={200: {'model': APIResponse}})
def add_label_with_note(request: Request, response: Response, data: schemas.LabelAssociate):
    try:
        note = dependencies.note_availability(note_id=data.note_id, user_id=request.state.user.get('_id'))
        labels = {}
        for label in data.labels:
            label_data = dependencies.fetch_label(label_id=label, user_id=request.state.user.get('_id'))
            if not label_data:
                raise Exception(f'Label {label} not found')
            labels.update({f'labels.{label_data["_id"]["$oid"]}': [{'$ref': 'label',
                                                                    '$id': label_data["_id"]["$oid"],
                                                                    '$db': 'fundoo_microservices'},
                                                                   {'title': label_data['title']}]})
        note = Notes.find_one_and_update(note, {'$set': labels})
        return {'message': 'Label associated with note', 'status': 200, 'data': {}}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex), 'status': response.status_code, 'data': {}}


@router.delete('/deleteLabelFromNote/', status_code=status.HTTP_200_OK, response_class=JSONResponse,
               responses={200: {'model': APIResponse}})
def delete_label_from_note(request: Request, response: Response, data: schemas.LabelAssociate):
    try:
        note = dependencies.note_availability(note_id=data.note_id, user_id=request.state.user.get('_id'))
        labels = {}
        for label in data.labels:
            label_data = dependencies.fetch_label(label_id=label, user_id=request.state.user.get('_id'))
            if not label_data:
                raise Exception(f'Label {label} not found')
            labels.update({f'labels.{label_data["_id"]["$oid"]}': ""})
        Notes.update_one(note, {'$unset': labels})
        return {'message': 'Label removed from note', 'status': 200, 'data': {}}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex), 'status': response.status_code, 'data': {}}
