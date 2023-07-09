from user.app.password import set_password


def get_db(session_local):
    db = session_local()
    try:
        yield db
        db.commit()
    finally:
        db.close()


def session_handler(function):
    def wrapper(instance=None, *args, **kwargs):
        session = instance.session
        try:
            return function(instance, *args, **kwargs)
        except:
            session.rollback()
            raise
        finally:
            session.close()

    return wrapper


class Manager:
    def __init__(self, session) -> None:
        self.model = None
        self.get_session = get_db(session)
        self.session = next(self.get_session)

    def __set_name__(self, owner, name):
        self.model = owner

    @session_handler
    def create(self, **payload):
        instance = self.model(**payload)
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    @session_handler
    def create_user(self, **payload):
        if 'password' not in payload.keys():
            raise Exception('Password field required')
        payload['password'] = set_password(payload['password'])
        instance = self.create(**payload)
        return instance

    @session_handler
    def add(self, instance):
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)

    @session_handler
    def bulk_create(self, *instances):
        self.session.add_all(*instances)
        self.session.commit()

    @session_handler
    def update(self, **payload):
        # instance = self.get(id=payload.get("id"))
        instance = self.session.query(self.model).filter_by(id=payload.get("id")).one()
        for k, v in payload.items():
            setattr(instance, k, v)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    @session_handler
    def delete(self, **payload):
        # instance = self.get(id=payload.get("id"))
        instance = self.session.query(self.model).filter_by(id=payload.get("id")).one()
        self.session.delete(instance)
        self.session.commit()

    @session_handler
    def get(self, **payload):
        instance = self.session.query(self.model).filter_by(**payload).one()
        return instance

    @session_handler
    def get_or_none(self, **payload):
        instance = self.session.query(self.model).filter_by(**payload).one_or_none()
        return instance

    @session_handler
    def filter(self, **payload):
        instance_list = self.session.query(self.model).filter_by(**payload).all()
        return instance_list

    @session_handler
    def all(self):
        instance_list = self.session.query(self.model).all()
        return instance_list

    @session_handler
    def save(self):
        self.session.commit()
