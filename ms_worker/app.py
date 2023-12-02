from services import queue_service, TASKS_TOPIC
from flask_restful import Api
from flask import Flask
import os
import threading
from views.views import ViewHealth

app = Flask(__name__)
api = Api(app)

api.add_resource(ViewHealth, '/api/health')

def run_consumer():
    queue_service.listener_queue(TASKS_TOPIC)

consumer_thread = threading.Thread(target=run_consumer)
consumer_thread.start()

if __name__ == '__main__':
    app.run(debug=True)