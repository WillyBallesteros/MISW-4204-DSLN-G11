from services import queue_service, TASKS_QUEUE
from flask import Flask
import os
import threading

app = Flask(__name__)

def run_consumer():
    queue_service.listener_queue(TASKS_QUEUE)

consumer_thread = threading.Thread(target=run_consumer)
consumer_thread.start()

if __name__ == '__main__':
    app.run(debug=True)