import json
import concurrent.futures
from datetime import datetime
from models.models import db, Task
from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.subscriber.scheduler import ThreadScheduler
from . import PROJECT_ID

publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()

def listener_queue(app, subscription_id):
    subscription_path = subscriber.subscription_path(PROJECT_ID, subscription_id)
    flow_control = pubsub_v1.types.FlowControl(max_messages=1)
    scheduler = ThreadScheduler(executor=concurrent.futures.ThreadPoolExecutor(max_workers=1))

    def callback(message):
        message.modify_ack_deadline(300)
        body = message.data.decode("utf-8")
        print(f"Received event: {body}.")
        bodyData = json.loads(body)
        event = bodyData.get('event')
        if event == "TASK_COMPLETED":
            data = bodyData.get('payload')
            task_id = data.get('task_id')
            start_process = data.get('start_process')
            end_process = data.get('end_process')
            ok = data.get('success')
            
            msg = data.get('message')
            with app.app_context():
                task = Task.query.filter_by(id=task_id).first()
                if task: 
                    task.status = "processed"
                    task.start_process_date = datetime.strptime(start_process, '%Y-%m-%d %H:%M:%S.%f')
                    task.finish_process_date = datetime.strptime(end_process, '%Y-%m-%d %H:%M:%S.%f')
                    task.completed_process_date = datetime.now()
                    task.process_successful = ok
                    task.process_message = msg,
                    db.session.commit()   
        message.ack()

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback, flow_control=flow_control, scheduler=scheduler)

    print(f" [*] Waiting for events in topic: {subscription_path}.")
    try:
        streaming_pull_future.result()
    except KeyboardInterrupt as e:
        print(f"Subscription failed: {e}")
        streaming_pull_future.cancel()

def send_message(data, topic_id):
    topic_path = publisher.topic_path(PROJECT_ID, topic_id)
    data = data.encode("utf-8")
    future = publisher.publish(topic_path, data)
    message_id = future.result()
    print(f"Send {data} to {topic_path} with message_id = {message_id}")
    
