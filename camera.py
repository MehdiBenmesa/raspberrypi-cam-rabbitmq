from time import time
import pika
import uuid


class Camera(object):

    def __init__(self):
        # to connect to a broker on a different machine use the following lines
        # you'll also need to create a new user named "test" with admin grants on rabbitmq server
        # and to put the ip address of the raspberry 
        # credentials = pika.PlainCredentials('test','test')
        # parameters = pika.ConnectionParameters('192.168.1.6', 5672, '/', credentials)
        parameters = pika.ConnectionParameters(host='localhost')
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue) 
        self.frames = [open(f + '.jpg', 'rb').read() for f in ['1', '2', '3']]

    def get_frame(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='cam1',
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ), body = str(1))
        while self.response is None:
            self.connection.process_data_events()
        return self.frames.pop(0)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            print("recieved")
            self.frames.append(body)
            self.response = body
