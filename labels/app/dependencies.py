from core.monogodb import Label
from bson.objectid import ObjectId


def fetch_label(payload: dict):
    try:
        label = Label.find_one({'_id': ObjectId(payload.get('label')), 'user': ObjectId(payload.get('user'))})
    except Exception as ex:
        raise ex
    return label
