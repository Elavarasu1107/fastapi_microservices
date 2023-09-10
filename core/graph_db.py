from neomodel import (config, StructuredNode, StringProperty, IntegerProperty,
                      RelationshipTo, UniqueProperty, UniqueIdProperty, BooleanProperty)

config.DATABASE_URL = 'bolt://neo4j:Zeus.1996@localhost:7687'


class User(StructuredNode):
    id = UniqueIdProperty()
    username = StringProperty(unique=True, required=True)
    password = StringProperty(required=True)
    first_name = StringProperty(required=False)
    last_name = StringProperty(required=False)
    email = StringProperty(required=True)
    phone = IntegerProperty(required=False)
    location = StringProperty(default=None)
    is_superuser = BooleanProperty(default=False)
    is_verified = BooleanProperty(default=False)

