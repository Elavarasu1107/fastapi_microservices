from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    String,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from settings import settings

LabelBase = declarative_base()
label_engine = create_engine(settings.notedb_url)
LabelBase.metadata.create_all(label_engine)
SessionLocal = sessionmaker(bind=label_engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    finally:
        db.close()


session = get_db()
session = next(session)


def get_session(function):
    def wrapper(instance=None, *args, **kwargs):
        try:
            return function(instance, *args, **kwargs)
        except:
            session.rollback()
            raise
        finally:
            session.close()
    return wrapper


class Manager:
    def __init__(self) -> None:
        self.model = None

    def __set_name__(self, owner, name):
        self.model = owner

    @get_session
    def create(self, **payload):
        instance = self.model(**payload)
        session.add(instance)
        session.commit()
        session.refresh(instance)
        return instance

    @get_session
    def add(self, instance):
        session.add(instance)
        session.commit()
        session.refresh(instance)

    @get_session
    def bulk_create(self, *instances):
        session.add_all(*instances)
        session.commit()

    @get_session
    def update(self, **payload):
        instance = self.get(id=payload.get("id"))
        for k, v in payload.items():
            setattr(instance, k, v)
        session.commit()
        session.refresh(instance)
        return instance

    @get_session
    def delete(self, **payload):
        instance = self.get(id=payload.get("id"))
        session.delete(instance)
        session.commit()

    @get_session
    def get(self, **payload):
        instance = session.query(self.model).filter_by(**payload).one()
        return instance

    @get_session
    def get_or_none(self, **payload):
        instance = session.query(self.model).filter_by(**payload).one_or_none()
        return instance

    @get_session
    def filter(self, **payload):
        instance_list = session.query(self.model).filter_by(**payload).all()
        return instance_list

    @get_session
    def all(self):
        instance_list = session.query(self.model).all()
        return instance_list

    @get_session
    def save(self):
        session.commit()


class Labels(LabelBase):
    __tablename__ = "labels"

    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(String(150))
    color = Column(String(150))
    objects = Manager()

    def __repr__(self):
        return f"Labels(id={self.id!r})"

    def to_dict(self):
        return {"id": self.id, "title": self.title, "color": self.color}

