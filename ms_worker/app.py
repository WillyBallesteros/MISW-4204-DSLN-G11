from services import queue_service, TASKS_TOPIC
from flask import Flask
import os
import threading

app = Flask(__name__)

def run_consumer():
    queue_service.listener_queue(TASKS_TOPIC)

consumer_thread = threading.Thread(target=run_consumer)
consumer_thread.start()

if __name__ == '__main__':
    app.run(debug=True)