from neomodel import (config, StructuredNode, StringProperty, IntegerProperty, StructuredRel,
                      RelationshipTo, UniqueIdProperty, BooleanProperty, DateTimeFormatProperty, RelationshipFrom)
from settings import settings
from neomodel.scripts.neomodel_install_labels import load_python_module_or_file, main

config.DATABASE_URL = settings.neo_uri


class Collaborator(StructuredRel):
    grant_access = BooleanProperty(default=False)


class Creator(StructuredRel):
    created_at = DateTimeFormatProperty(default_now=True, format='%Y-%m-%dT%H:%M:%SZ')
    updated_at = DateTimeFormatProperty(format='%Y-%m-%dT%H:%M:%SZ', required=False)


class User(StructuredNode):
    id = UniqueIdProperty()
    username = StringProperty(unique_index=True, required=True)
    password = StringProperty(required=True)
    first_name = StringProperty(required=False)
    last_name = StringProperty(required=False)
    email = StringProperty(required=True)
    phone = IntegerProperty(required=False)
    location = StringProperty(default=None)
    is_superuser = BooleanProperty(default=False)
    is_verified = BooleanProperty(default=False)
    notes = RelationshipFrom('Note', 'CREATED_BY')
    collab_notes = RelationshipFrom('Note', 'COLLABORATED_TO')
    label = RelationshipFrom('Label', 'CREATED_BY')

    @property
    def json(self):
        return self.__dict__


class Note(StructuredNode):
    id = UniqueIdProperty()
    title = StringProperty()
    description = StringProperty()
    reminder = DateTimeFormatProperty(default=None, format='%Y-%m-%dT%H:%M:%SZ')
    user = RelationshipTo(User, 'CREATED_BY')
    collaborator = RelationshipTo(User, 'COLLABORATED_TO', model=Collaborator)
    labels = RelationshipFrom('Label', 'ASSOCIATED_WITH')


class Label(StructuredNode):
    id = UniqueIdProperty()
    title = StringProperty()
    color = StringProperty()
    user = RelationshipTo(User, 'CREATED_BY')
    notes = RelationshipTo(Note, 'ASSOCIATED_WITH')


load_python_module_or_file(__name__)
