from redbeat import RedBeatSchedulerEntry as Task
from celery.schedules import crontab
from core.tasks import celery
from core.graph_db import Note, Label


def fetch_label(label_id, user):
    label = Label.nodes.get_or_none(id=label_id)
    if not label.user.is_connected(user):
        return None
    return label


def note_availability(note_id, user):
    note = Note.nodes.get_or_none(id=note_id)
    if not note:
        raise Exception('Note not found')
    if not note.user.is_connected(user) and not note.collaborator.is_connected(user) and \
            user not in note.collaborator.match(grant_access=True).all():
        raise Exception('Note not found or permission denied')
    return note


def send_reminder(payload, reminder, task_name):
    task = Task(name=task_name,
                task='core.tasks.send_mail',
                schedule=crontab(month_of_year=reminder.month,
                                 day_of_month=reminder.day,
                                 hour=reminder.hour,
                                 minute=reminder.minute),
                app=celery, args=[payload])
    task.save()
