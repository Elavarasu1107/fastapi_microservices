from pydantic import BaseSettings, PostgresDsn
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

    class Config:
        env_file = ".env"


settings = Settings()

logging.basicConfig(filename='fundoo.log', encoding='utf-8', level=logging.WARNING,
                    format='%(asctime)s:%(filename)s:%(levelname)s:%(lineno)d:%(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger()
