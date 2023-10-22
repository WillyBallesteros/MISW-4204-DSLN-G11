import pika
import json
from flask import current_app
from datetime import datetime
from models.models import db, Task
from . import RABBITMQ_HOST, EVENTS_QUEUE, PROCESS_ID

def listener_queue(app, queue_name):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)

    def callback(ch, method, properties, body):
        print(f"Received event: {body}.")
        bodyData = json.loads(body)
        event = bodyData.get('event')
        if event == "TASK_COMPLETED":
            data = bodyData.get('payload')
            task_id = data.get('task_id')
            start_process = data.get('start_process')
            end_process = data.get('end_process')
            with app.app_context():
                task = Task.query.filter_by(id=task_id).first()
                if task: 
                    task.status = "processed"
                    task.start_process_date = datetime.strptime(start_process, '%Y-%m-%d %H:%M:%S.%f')
                    task.finish_process_date = datetime.strptime(end_process, '%Y-%m-%d %H:%M:%S.%f')
                    task.completed_process_date = datetime.now(),
                    db.session.commit()       

    channel.basic_consume(queue=queue_name,
                          on_message_callback=callback,
                          auto_ack=True)

    print(f" [*] Waiting for events in queue: {queue_name}.")
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