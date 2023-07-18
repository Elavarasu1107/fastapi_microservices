from celery import Celery
from .rmq_producer import Producer
from settings import settings


celery = Celery(__name__,
                broker=settings.celery_broker,
                backend=settings.celery_result,
                broker_connection_retry_on_startup=True)


@celery.task()
def send_mail(method, payload):
    producer = Producer()
    producer.publish(method=method, payload=payload)
    return producer.response
