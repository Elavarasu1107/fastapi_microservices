#!/usr/bin/env python
import pika
import json
import os
from dotenv import load_dotenv

load_dotenv()


class Producer:

    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        list(map(lambda x: self.channel.queue_declare(x, durable=True), os.environ.get('QUEUES').split(',')))

    def publish(self, method, payload):
        payload_bytes = json.dumps(payload).encode('UTF-8')
        self.channel.basic_publish(exchange='',
                                   routing_key=method,
                                   body=payload_bytes,
                                   properties=pika.BasicProperties(method))
        self.connection.close()
