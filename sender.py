#!/usr/bin/env python
import argparse
import pika
import cv2
from PIL import Image
try:
    import cStringIO as io
except ImportError:
    import io

parser = argparse.ArgumentParser(description="Starts a webserver that "
                                 "connects to a webcam.")

args = parser.parse_args()

camera = cv2.VideoCapture(0)
camera.set(3, 640)
camera.set(4, 480)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue = 'cam1')
sio = io.StringIO()

def on_request(ch, method, props, body):
    _, frame = camera.read()
    ret, jpeg = cv2.imencode('.jpg', frame)
    print("send")
    ch.basic_publish(exchange = '', 
                     routing_key = props.reply_to, 
                     properties = pika.BasicProperties(correlation_id = props.correlation_id),
                     body = jpeg.tobytes())
    ch.basic_ack(delivery_tag = method.delivery_tag) 

channel.basic_qos(prefetch_count = 1)
channel.basic_consume(on_request, queue = 'cam1')
print ("waiting")
channel.start_consuming()
