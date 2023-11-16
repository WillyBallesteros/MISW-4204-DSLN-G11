import threading
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_cors import CORS
from models import db
from views.views import ViewHealth, ViewCreateUser, ViewLogIn, ViewTasks, ViewDownloadVideo, ViewTask
from services import queue_service, DATABASE_URL, EVENTS_TOPIC, JWT_SECRET


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['JWT_SECRET_KEY'] = JWT_SECRET

app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

cors = CORS(app)

api = Api(app)
api.add_resource(ViewHealth, '/api/health')
api.add_resource(ViewCreateUser, '/api/auth/signup')
api.add_resource(ViewLogIn, '/api/auth/login')
api.add_resource(ViewDownloadVideo, '/api/download/<string:uuid>/<string:resource>')
api.add_resource(ViewTasks, '/api/tasks')
api.add_resource(ViewTask, '/api/tasks/<int:task_id>')

def run_consumer():
    queue_service.listener_queue(app, EVENTS_TOPIC)

consumer_thread = threading.Thread(target=run_consumer)
consumer_thread.start()


if __name__ == '__main__':
    app.run(debug=True)

jwt = JWTManager(app)