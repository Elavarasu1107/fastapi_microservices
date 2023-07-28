from pydantic import BaseSettings, PostgresDsn, EmailStr
import logging


class Settings(BaseSettings):
    userdb_url: PostgresDsn
    notedb_url: PostgresDsn
    labeldb_url: PostgresDsn
    algorithm: str
    jwt_key: str
    base_url: str
    user_port: int
    note_port: int
    label_port: int
    celery_broker: str
    celery_result: str
    admin_key: str
    email_host_user: EmailStr
    email_host_password: str
    smtp: str
    smtp_port: int

    class Config:
        env_file = ".env"


settings = Settings()

logging.basicConfig(filename='fundoo.log', encoding='utf-8', level=logging.WARNING, filemode='w',
                    format='%(asctime)s:%(filename)s:%(levelname)s:%(lineno)d:%(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger()
