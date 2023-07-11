from fastapi import FastAPI
from user.app.views import router as ur
from notes.app.views import router as nr
from labels.app.views import router as lr


user_app = FastAPI(title='Fundoo User')
note_app = FastAPI(title='Fundoo Notes')
label_app = FastAPI(title='Fundoo Label')

user_app.include_router(ur, tags=['User'])
note_app.include_router(nr, prefix='/note', tags=['Note'])
label_app.include_router(lr, prefix='/label', tags=['Label'])
