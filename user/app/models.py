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

UserBase = declarative_base()
user_engine = create_engine(settings.userdb_url)
UserBase.metadata.create_all(user_engine)
SessionLocal = sessionmaker(bind=user_engine, autoflush=False, autocommit=False)


class User(UserBase):
    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(250), unique=True)
    password = Column(String(250))
    first_name = Column(String(250))
    last_name = Column(String(250))
    email = Column(String(150))
    phone = Column(BigInteger)
    location = Column(String(150))
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)

    objects = manager.Manager(SessionLocal)

    def save(self):
        self.objects.save()

    def __repr__(self):
        return f"User({self.id})"

    def to_dict(self):
        return {"id": self.id, "username": self.username, "first_name": self.first_name, "last_name": self.last_name,
                "email": self.email, "phone": self.phone, "location": self.location}
