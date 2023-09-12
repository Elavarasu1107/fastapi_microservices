from bson import ObjectId
from fastapi import APIRouter, Request, Response, status, Depends, Security, HTTPException
from fastapi.security import APIKeyHeader
from . import schemas, dependencies
from .models import Labels, LabelCollab
from settings import logger, settings
from fastapi.responses import JSONResponse
from core.utils import APIResponse
from user.app import auth
from core.graph_db import Label


router = APIRouter(dependencies=[Security(APIKeyHeader(name='Authorization', auto_error=False)),
                                 Depends(auth.check_user)])


@router.post('/create/', status_code=status.HTTP_201_CREATED, response_class=JSONResponse,
             responses={201: {'model': APIResponse}})
def create_label(request: Request, data: schemas.LabelSchema, response: Response):
    try:
        data = data.dict()
        label = Label(**data).save()
        label.user.connect(request.state.user)
        label = schemas.LabelResponse.from_orm(label)
        return {'message': 'Label created', 'status': 201, 'data': label}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex), 'status': response.status_code, 'data': {}}


@router.get("/get/", status_code=status.HTTP_200_OK, response_class=JSONResponse,
            responses={200: {'model': APIResponse}})
def get_label(request: Request, response: Response):
    try:
        labels = request.state.user.label.all()
        labels = [schemas.LabelResponse.from_orm(i) for i in labels]
        return {'message': 'Labels retrieved', 'status': 200, 'data': labels}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex), 'status': response.status_code, 'data': {}}


@router.get("/retrieve/", status_code=status.HTTP_200_OK, response_class=JSONResponse,
            responses={200: {'model': APIResponse}})
def retrieve(request: Request, response: Response, note_id: int):
    try:
        associate_label = LabelCollab.objects.filter(note_id=note_id)
        associate_label = [Labels.objects.get(id=x.label_id).title for x in associate_label]
        return {'message': 'Labels retrieved', 'status': 200, 'data': associate_label}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex)}


@router.put("/update/", status_code=status.HTTP_200_OK, response_class=JSONResponse,
            responses={200: {'model': APIResponse}})
def update_label(request: Request, response: Response, label_id: str, data: schemas.LabelSchema):
    try:
        data = data.dict()
        label = Label.nodes.get_or_none(id=label_id)
        if not label or not label.user.is_connected(request.state.user):
            raise Exception('Label not found')
        [setattr(label, x, y) for x, y in data.items()]
        label.save()
        label = schemas.LabelResponse.from_orm(label)
        return {'message': 'Label updated', 'status': 200, 'data': label}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex), 'status': response.status_code, 'data': {}}


@router.delete("/delete/", status_code=status.HTTP_200_OK, response_class=JSONResponse,
               responses={200: {'model': APIResponse}})
def delete_label(request: Request, response: Response, label_id: str):
    try:
        label = Label.nodes.get_or_none(id=label_id)
        if not label or not label.user.is_connected(request.state.user):
            raise Exception('Label not found')
        label.delete()
        return {'message': 'Label deleted', 'status': 200, 'data': {}}
    except Exception as ex:
        logger.exception(ex)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(ex), 'status': response.status_code, 'data': {}}
