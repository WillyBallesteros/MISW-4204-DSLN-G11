import os
import pika
import json
from flask import current_app
import datetime
from services.video_service import convert_video
from . import RABBITMQ_HOST, EVENTS_QUEUE, PROCESS_ID

def listener_queue(queue_name):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)

    def callback(ch, method, properties, body):
        print(f"Received task: {body}.")
        bodyData = json.loads(body)
        action = bodyData.get('action')
        if action == "RUN_TASK":
          data = bodyData.get('payload')
          input = data.get('input')
          output = data.get('output')
          codec = data.get('codec')
          task_id = data.get('task_id')
          if not os.path.exists(input):
            print(f"Task {task_id} was previously deleted ")  
            return
          
          start_process = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
          error = convert_video(input, output, codec)
          end_process = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
          message = ""
          success = True
          if error != None:
              message = str(error)
              success = False

          send_message(json.dumps({
            "source": PROCESS_ID,
            "event": "ENDED_TASK",
            "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "payload": {
              "task_id": task_id,
              "success": success,
              "message": message,
              "start_process": start_process,
              "end_process": end_process,
            }
          }), EVENTS_QUEUE)

    channel.basic_consume(queue=queue_name,
                          on_message_callback=callback,
                          auto_ack=True)

    print(f" [*] Waiting for tasks in queue: {queue_name}. To exit press CTRL+C")
    channel.start_consuming()

def send_message(message, queue_name):
    print(f"Send {message} to {queue_name}")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='',
            routing_key=queue_name,
            body=message)
    
    connection.close()