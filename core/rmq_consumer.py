#!/usr/bin/env python
import pika
import json
import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv
from os import environ
import sys
from bson import json_util
sys.path.append('./')

from user.app import auth
from labels.app import dependencies
from settings import logger

load_dotenv()


class Consumer:

    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=environ.get('RMQ_HOST')))
        # self.connection = pika.BlockingConnection(pika.URLParameters(environ.get('RMQ_URL')))
        self.channel = self.connection.channel()
        self.callbacks = {i: getattr(self, i) for i in dir(self) if i.startswith('cb_') and callable(getattr(self, i))}
        tuple(map(lambda x: self.channel.queue_declare(queue=x), self.callbacks.keys()))

    def cb_check_user(self, ch, method, properties, body):
        try:
            user_data = auth.api_key_authenticate(json.loads(body), auth.Audience.login.value)
            message = None
            if user_data:
                user_data['_id'] = str(user_data['_id'])
                message = user_data['_id']
            else:
                user_data = {}
                message = "User not found"
            ch.basic_publish(
                exchange='',
                routing_key=properties.reply_to,
                properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                body=json.dumps(user_data)
            )
            print(f'{message}: verified and sent response successfully')
        except Exception as ex:
            print(ex)
            logger.exception(ex)

    def cb_check_label(self, ch, method, properties, body):
        try:
            label_data = dependencies.fetch_label(json.loads(body))
            message = None
            if label_data:
                message = label_data['_id']
            else:
                label_data = {}
                message = "Label not found"
            ch.basic_publish(
                exchange='',
                routing_key=properties.reply_to,
                properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                body=json_util.dumps(label_data)
            )
            print(f'{message}: verified and sent response successfully')
        except Exception as ex:
            print(ex)
            logger.exception(ex)

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
