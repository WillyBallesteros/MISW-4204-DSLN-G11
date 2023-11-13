import os
import pika
import json
from flask import current_app
from google.cloud import storage
import datetime
from services.video_service import convert_video
from . import RABBITMQ_HOST, EVENTS_QUEUE, PROCESS_ID, RABBITMQ_TIMEOUT, TMP_PATH

def listener_queue(queue_name):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, heartbeat=RABBITMQ_TIMEOUT))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)

    def callback(ch, method, properties, body):
        print(f"Received task: {body}.")
        bodyData = json.loads(body)
        action = bodyData.get('action')
        if action == "NEW_TASK":
          data = bodyData.get('payload')
          input = data.get('input')
          output = data.get('output')
          codec = data.get('codec')
          task_id = data.get('task_id')
          #if not os.path.exists(input):
          #  print(f"Task {task_id} was previously deleted ")  
          #  return
          
          start_process = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

          bucket = input.split('/')[3]
          inputBucket = input.split('/')[4]
          inputPath = f"{TMP_PATH}/{inputBucket}"
          storage_client = storage.Client()
          bucket = storage_client.get_bucket(bucket)
          source_blob = bucket.blob(inputBucket)
          if not source_blob.exists():
            print(f"Task {task_id} was previously deleted ")  
            return

          source_blob.download_to_filename(inputPath)

          outputBucket = output.split('/')[4]
          outputPath = f"{TMP_PATH}/{outputBucket}"
          
          error = convert_video(inputPath, outputPath, codec)
          os.remove(inputPath)
        
          if error is None:
            new_blob = bucket.blob(outputBucket)
            new_blob.upload_from_filename(outputPath)
            new_blob.make_public()
            os.remove(outputPath)

          end_process = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
          message = ""
          success = True
          if error != None:
              message = str(error)
              success = False

          send_message(json.dumps({
            "source": PROCESS_ID,
            "event": "TASK_COMPLETED",
            "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
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
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, heartbeat=RABBITMQ_TIMEOUT))
    channel = connection.channel()
    
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='',
            routing_key=queue_name,
            body=message)
    
    connection.close()
