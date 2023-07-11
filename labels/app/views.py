from fastapi import APIRouter, Request, Response, status, Depends, Security, HTTPException
from fastapi.security import APIKeyHeader
from . import schemas, dependencies
from .models import Labels, LabelCollab
from settings import logger, settings
from fastapi.responses import JSONResponse
from core.utils import APIResponse

router = APIRouter(dependencies=[Security(APIKeyHeader(name='Authorization', auto_error=False)),
                                 Depends(dependencies.check_user)])


@router.post('/create/', status_code=status.HTTP_201_CREATED, response_class=JSONResponse,
             responses={201: {'model': APIResponse}})
def create_label(request: Request, data: schemas.LabelSchema, response: Response):
    try:
        data = data.dict()
        data.update({'user_id': request.state.user.get('id')})
        label = Labels.objects.create(**data)
        return {'message': 'Label created', 'status': 201, 'data': label.to_dict()}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex), 'status': response.status_code, 'data': {}}


@router.get("/get/", status_code=status.HTTP_200_OK, response_class=JSONResponse,
            responses={200: {'model': APIResponse}})
def get_label(request: Request, response: Response):
    try:
        labels = list(map(lambda x: x.to_dict(), Labels.objects.filter(user_id=request.state.user.get('id'))))
        return {'message': 'Labels retrieved', 'status': 200, 'data': labels}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex), 'status': response.status_code, 'data': {}}


@router.put("/update/", status_code=status.HTTP_200_OK, response_class=JSONResponse,
            responses={200: {'model': APIResponse}})
def update_label(request: Request, response: Response, label_id: int, data: schemas.LabelSchema):
    try:
        data = data.dict()
        data.update({'id': label_id, 'user_id': request.state.user.get('id')})
        label = Labels.objects.update(**data)
        return {'message': 'Label updated', 'status': 200, 'data': label.to_dict()}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex), 'status': response.status_code, 'data': {}}


@router.delete("/delete/", status_code=status.HTTP_200_OK, response_class=JSONResponse,
               responses={200: {'model': APIResponse}})
def delete_label(request: Request, response: Response, label_id: int):
    try:
        Labels.objects.delete(id=label_id, user_id=request.state.user.get('id'))
        return {'message': 'Label deleted', 'status': 200, 'data': {}}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex), 'status': response.status_code, 'data': {}}


@router.post('/addLabelWithNote/', status_code=status.HTTP_200_OK, response_class=JSONResponse,
             responses={200: {'model': APIResponse}})
def add_label_with_note(request: Request, response: Response, data: schemas.LabelAssociate):
    try:
        note = dependencies.fetch_note(note_id=data.note_id, token=request.headers.get('authorization'))
        if not note:
            raise Exception('Note not found')
        labels = []
        for i in data.labels:
            label = Labels.objects.get_or_none(id=i, user_id=request.state.user.get('id'))
            if not label:
                raise Exception(f'Label {i} not found')
            labels.append(LabelCollab(note_id=note.get('id'), label_id=label.id))
        LabelCollab.objects.bulk_create(labels)
        return {'message': 'Label associated with note', 'status': 200, 'data': {}}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex), 'status': response.status_code, 'data': {}}


@router.delete('/deleteLabelFromNote/', status_code=status.HTTP_200_OK, response_class=JSONResponse,
               responses={200: {'model': APIResponse}})
def delete_label_from_note(request: Request, response: Response, data: schemas.LabelAssociate):
    try:
        note = dependencies.fetch_note(note_id=data.note_id, token=request.headers.get('authorization'))
        if not note:
            raise Exception('Note not found')
        labels = []
        for i in data.labels:
            label = Labels.objects.get_or_none(id=i, user_id=request.state.user.get('id'))
            if not label:
                raise Exception(f'Label {i} not found')
            collab_label = LabelCollab.objects.get_or_none(note_id=note.get('id'), label_id=label.id)
            if not collab_label:
                raise Exception(f'Label {i} is not associated with note')
            labels.append(collab_label)
        [LabelCollab.objects.delete(id=x.id) for x in labels]
        return {'message': 'Label removed from note', 'status': 200, 'data': {}}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex), 'status': response.status_code, 'data': {}}
