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
    mongo_host: str
    mongo_port: int
    mongo_db_name: str

    class Config:
        env_file = ".env"


settings = Settings()

# logging.basicConfig(filename='fundoo.log', encoding='utf-8', level=logging.WARNING, filemode='w',
#                     format='%(asctime)s:%(filename)s:%(levelname)s:%(lineno)d:%(message)s',
#                     datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger()

formatter = logging.Formatter(fmt='%(asctime)s:%(filename)s:%(levelname)s:%(lineno)d:%(message)s',
                              datefmt='%m/%d/%Y %I:%M:%S %p')

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(formatter)

file = logging.FileHandler('fundoo.log')
file.setLevel(logging.WARNING)
file.setFormatter(formatter)

logger.addHandler(console)
logger.addHandler(file)
