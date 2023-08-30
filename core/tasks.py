import smtplib
import ssl
from email.message import EmailMessage
from celery import Celery
from settings import settings


celery = Celery(__name__,
                broker=settings.celery_broker,
                backend=settings.celery_result,
                broker_connection_retry_on_startup=True,
                redbeat_redis_url=settings.celery_broker,
                redbeat_lock_key=None,
                enable_utc=False,
                beat_max_loop_interval=5,
                beat_scheduler='redbeat.schedulers.RedBeatScheduler')


@celery.task()
def send_mail(payload):
    msg = EmailMessage()
    msg['From'] = settings.email_host_user
    msg['To'] = payload.get('recipient')
    msg['Subject'] = payload.get('subject')
    msg.set_content(payload.get('message'))
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(settings.smtp, settings.smtp_port, context=context) as smtp:
        smtp.login(user=settings.email_host_user, password=settings.email_host_password)
        smtp.sendmail(settings.email_host_user, payload.get('recipient'), msg.as_string())
        smtp.quit()
    print(f"Mail sent to {payload.get('recipient')}")
