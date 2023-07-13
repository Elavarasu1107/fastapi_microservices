from sqlalchemy import (
    BigInteger,
    Column,
    String,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from settings import settings
from core import manager

NoteBase = declarative_base()
note_engine = create_engine(settings.notedb_url)
NoteBase.metadata.create_all(note_engine)
SessionLocal = sessionmaker(bind=note_engine, autoflush=False, autocommit=False)


class Notes(NoteBase):
    __tablename__ = "notes"

    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(String(150))
    description = Column(String(150))
    user_id = Column(BigInteger, nullable=False)
    objects = manager.Manager(SessionLocal)

    def save(self):
        self.objects.save()

    def __repr__(self):
        return f"Notes({self.id!r})"

    def to_dict(self):
        return {"id": self.id, "title": self.title, "description": self.description, "user_id": self.user_id}


class Collaborator(NoteBase):
    __tablename__ = 'collaborator'

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False)
    note_id = Column(BigInteger, nullable=False)
    objects = manager.Manager(SessionLocal)

    def save(self):
        self.objects.save()

    def __str__(self):
        return f'Collaborator({self.id})'
