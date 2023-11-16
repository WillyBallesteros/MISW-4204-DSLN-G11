import os
import json
from google.cloud import storage
import datetime
from services.video_service import convert_video
from google.cloud import pubsub_v1
from . import PROJECT_ID, EVENTS_TOPIC, PROCESS_ID, TMP_PATH

publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()

def listener_queue(subscription_id):
    subscription_path = subscriber.subscription_path(PROJECT_ID, subscription_id)
    def callback(message):
        message.modify_ack_deadline(300)
        body = message.data.decode("utf-8")
        print(f"Received task: {body}.")
        bodyData = json.loads(body)
        action = bodyData.get('action')
        if action == "NEW_TASK":
          data = bodyData.get('payload')
          input = data.get('input')
          output = data.get('output')
          codec = data.get('codec')
          task_id = data.get('task_id')
          
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
          }), EVENTS_TOPIC)

        message.ack()

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f" [*] Waiting for events in topic: {subscription_path}.")
    try:
        streaming_pull_future.result()
    except KeyboardInterrupt as e:
        print(f"Subscription failed: {e}")
        streaming_pull_future.cancel()
        
def send_message(message, topic_id):
    topic_path = publisher.topic_path(PROJECT_ID, topic_id)
    data = data.encode("utf-8")
    future = publisher.publish(topic_path, data)
    message_id = future.result()
    print(f"Send {data} to {topic_path} with message_id = {message_id}")