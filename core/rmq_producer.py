#!/usr/bin/env python
import pika
import json
import uuid
import os
from dotenv import load_dotenv

load_dotenv()


class Producer:

    def __init__(self):
        # self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.connection = pika.BlockingConnection(pika.URLParameters(os.environ.get('RMQ_URL')))
        self.channel = self.connection.channel()
        self.reply_to = dict(map(lambda x: (f'reply_to_{x}', self.channel.queue_declare(f'reply_to_{x}')),
                                 os.environ.get('QUEUES').split(',')))
        self.callback_queue = dict(map(lambda x, y: (x, y.method.queue), self.reply_to.keys(), self.reply_to.values()))
        dict(map(lambda x, y: (x, self.channel.basic_consume(queue=x,
                                                             on_message_callback=self.on_response,
                                                             auto_ack=True)), self.callback_queue.keys(),
                 self.callback_queue.values()))
        self.queues = dict(map(lambda x: (x, self.channel.queue_declare(x)), os.environ.get('QUEUES').split(',')))
        self.response = None

    def map_publish(self, key, body):
        for i, j in self.queues.items():
            if i == key:
                corr_id = str(uuid.uuid4())
                self.channel.basic_publish(exchange='',
                                           routing_key=key,
                                           body=body,
                                           properties=pika.BasicProperties(
                                               reply_to=self.callback_queue.get(f'reply_to_{i}'),
                                               correlation_id=corr_id
                                           ))

    def publish(self, method, payload):
        payload_bytes = json.dumps(payload).encode('UTF-8')
        self.map_publish(method, payload_bytes)
        self.channel.start_consuming()

    def on_response(self, ch, method, props, body):
        self.response = json.loads(body)
        self.connection.close()
