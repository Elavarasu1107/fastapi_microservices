#!/usr/bin/env python
import pika
import json
import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv
from os import environ

load_dotenv()


class Consumer:

    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.sender = environ.get('EMAIL_HOST_USER')
        self.sender_password = environ.get('EMAIL_HOST_PASSWORD')
        self.callbacks = {i: getattr(self, i) for i in dir(self) if i.startswith('cb_') and callable(getattr(self, i))}
        tuple(map(lambda x: self.channel.queue_declare(queue=x, durable=True), self.callbacks.keys()))

    def cb_mailer(self, ch, method, properties, body):
        try:
            payload = json.loads(body.decode('UTF-8'))
            msg = EmailMessage()
            msg['From'] = self.sender
            msg['To'] = payload.get('recipient')
            msg['Subject'] = 'Rabbit Fastapi Microservices'
            msg.set_content(payload.get('message'))
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(environ.get('SMTP'), int(environ.get('SMTP_PORT')), context=context) as smtp:
                smtp.login(user=self.sender, password=self.sender_password)
                smtp.sendmail(self.sender, payload.get('recipient'), msg.as_string())
                smtp.quit()
                print("[*] Mail sent to ", payload.get('recipient'))
        except Exception as ex:
            print(ex)

    def cb_test(self,  ch, method, properties, body):
        try:
            pass
        except Exception as ex:
            print(ex)

    def receiver(self):
        [self.channel.basic_consume(queue=i, on_message_callback=j, auto_ack=True) for i, j in self.callbacks.items()]
        print('[*] Receive Server Started. To exit press CTRL+C')
        self.channel.start_consuming()


if __name__ == '__main__':
    try:
        consumer = Consumer()
        consumer.receiver()
    except KeyboardInterrupt:
        print("Connection closed")
