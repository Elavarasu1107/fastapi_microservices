from bson import ObjectId

from core.monogodb import Notes
from core.rmq_producer import Producer


def fetch_label(label_id, user_id):
    producer = Producer()
    producer.publish('cb_check_label', payload={'label': label_id, 'user': user_id})
    return producer.response


def note_availability(note_id, user_id):
    my_note = Notes.find_one({'_id': ObjectId(note_id), 'user': ObjectId(user_id)})
    note = None
    if not my_note:
        note = Notes.find_one({'_id': ObjectId(note_id),
                               f'collaborators.{user_id}': {'$exists': True}})
    if not my_note and not note:
        raise Exception('Note not found')
    if not my_note and not user_id in note.get('collaborators'):
        raise Exception('Cannot modify un-collaborated note')
    if not my_note and not note.get('collaborators').get(user_id)[1].get('grant_access'):
        raise Exception('Access denied to update this note')
    if my_note:
        note = my_note
    return note
