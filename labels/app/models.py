from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    String,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from settings import settings
from core import manager

LabelBase = declarative_base()
label_engine = create_engine(settings.labeldb_url)
LabelBase.metadata.create_all(label_engine)
SessionLocal = sessionmaker(bind=label_engine, autoflush=False, autocommit=False)


class Labels(LabelBase):
    __tablename__ = "labels"

    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(String(150))
    color = Column(String(150))
    user_id = Column(BigInteger, nullable=False)
    objects = manager.Manager(SessionLocal)

    def __repr__(self):
        return f"Label({self.id!r})"

    def to_dict(self):
        return {"id": self.id, "title": self.title, "color": self.color, 'user_id': self.user_id}

