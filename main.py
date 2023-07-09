from fastapi import FastAPI
from user.app.views import router as ur
from notes.app.views import router as nr


user_app = FastAPI(title='Fundoo User')
note_app = FastAPI(title='Fundoo Notes')

user_app.include_router(ur, tags=['User'])
note_app.include_router(nr, prefix='/note', tags=['Note'])
