#!/usr/bin/env python
import pika
import json
import uuid
import os
from dotenv import load_dotenv

load_dotenv()


class Producer:

    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.reply_to = list(map(lambda x: self.channel.queue_declare(f'reply_to_{x}'),
                                 os.environ.get('QUEUES').split(',')))
        self.callback_queue = list(map(lambda x: x.method.queue, self.reply_to))
        list(map(lambda x: self.channel.basic_consume(queue=x,
                                                      on_message_callback=self.on_response,
                                                      auto_ack=True), self.callback_queue))
        self.queues = list(map(lambda x: self.channel.queue_declare(x), os.environ.get('QUEUES').split(',')))
        self.response = None
        self.corr_id = None

    def publish(self, method, payload):
        self.response = None
        self.corr_id = [str(uuid.uuid4()) for _ in range(len(self.callback_queue))]
        print(f'Sending request {self.corr_id}')
        payload_bytes = json.dumps(payload).encode('UTF-8')
        [self.channel.basic_publish(exchange='',
                                    routing_key=method,
                                    body=payload_bytes,
                                    properties=pika.BasicProperties(
                                        reply_to=self.callback_queue[i],
                                        correlation_id=self.corr_id[i]
                                    )) for i in range(len(self.callback_queue))]
        self.channel.start_consuming()

    def on_response(self, ch, method, props, body):
        self.response = f'reply received {body}'
        self.connection.close()
