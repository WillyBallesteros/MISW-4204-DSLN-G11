import datetime
import json
import os
import uuid
from flask import request, send_file
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_restful import Resource
from services.queue_service import send_message
from . import DESTINATION_FILEPATH, SOURCE_FILEPATH
from models import db, User, UserSchema, Task, TaskSchema
from services import PROCESS_ID, TASKS_QUEUE, video_service
from werkzeug.security import generate_password_hash, check_password_hash
from utils import utils
import os



class ViewLogIn(Resource):
    # login
    def post(self):

        busines_schema = UserSchema()

        # Retrieve user and password from request
        user_name = request.json["user_name"]
        passwd = request.json["passwd"]


        # Retrieve user from database
        user_db = busines_schema.dump(User.query.filter_by(user_name=user_name).first())

        if not(user_db):
            return {"error": "User not found"}, 404

        # Verify password using Passlib
        if not check_password_hash(user_db['password'], passwd):
            return {"error": "Invalid password"}, 401

        claims = {
            "name": user_db['user_name']
        }
        access_token = create_access_token(identity=user_db['id'], additional_claims=claims)
        return {"message": "loing successful", "token": access_token, "id": user_db['id']}

class ViewCreateUser(Resource):
    # signup
    def post(self):
        # Retrieve user and password from request
        user_name = request.json["user_name"]
        passwd1 = request.json["passwd1"]
        passwd2 = request.json["passwd2"]
        email = request.json["email"]

        #validation form passwords equals
        if passwd1 != passwd2:
            return {"error": "Invalid password confirmation"}, 401

        #validation for password minimal security conditions
        if not utils.password_validation(passwd1):
            return {"error": "Invalid password minimal security conditions"}, 401

        if not utils.email_validation(email):
            return {"error": "Invalid email"}, 401

        # validation for user
        user_db = User.query.filter_by(user_name=user_name, email=email).first()
        if user_db is not None:
            return {"error": "Invalid user and email, the combination already exists"}, 401


        hash = generate_password_hash(passwd1)

        user = User(
            user_name = user_name,
            password =  hash,
            email= email
        )
        db.session.add(user)
        db.session.commit()
        return {"message": "User created", "info": user.id}

class ViewTask(Resource):
    @jwt_required()
    def get(self, task_id):
        task_schema = TaskSchema()
        task = task_schema.dump(Task.query.get_or_404(task_id))

        task['origin_download_link']= '/api/download/'+ task['uuid']+"/origin"
        task['destination_download_link']= '/api/download/'+ task['uuid']+"/destination"
        return task
    
    @jwt_required()
    def delete(self, task_id):
        #Delete task
        task = Task.query.filter_by(id=task_id).first()
        if task is None:
            return 'task not found', 404
        
        if os.path.exists(task.source_file_system):
            os.remove(task.source_file_system)
        
        if os.path.exists(task.destination_file_system):
            os.remove(task.destination_file_system)
        
        db.session.delete(task)
        db.session.commit()

        return {"message": "Task was deleted"}
    
class ViewTasks(Resource):
    @jwt_required()
    def post(self):
        #Check filename
        if 'fileName' not in request.files:
            return 'Filename cannot be empty', 400
        file = request.files['fileName']
        filename = file.filename
        if filename == '':
            return 'Filename cannot be empty', 400

        sourceType = utils.get_extension(filename)

        if not video_service.validate_format(sourceType):
            return 'fileName file extensión must be be MP4, WEBM, AVI, MPEG or WMV', 400
        
        #Check destination type
        destinationType = request.form.get("newFormat")
        if destinationType is None:
            return 'newFormat cannot be empty', 400

        destinationType = destinationType.lower()

        if sourceType == destinationType:
            return 'newFormat cannot be equal to file format', 400

        if not video_service.validate_format(destinationType):
            return 'newFormat must be MP4, WEBM, AVI, MPEG or WMV', 400

        guid = uuid.uuid4().hex + uuid.uuid4().hex

        sourceFileSystem = os.path.join(SOURCE_FILEPATH, f"{guid}.{sourceType}")
        destinationFileSystem = os.path.join(DESTINATION_FILEPATH,  f"{guid}.{destinationType}")

        #Store file
        file.save(sourceFileSystem)
        
        #Create task
        task = Task(
            file_name = filename,
            source_type = sourceType,
            destination_type = destinationType,
            source_file_system = sourceFileSystem,
            destination_file_system = destinationFileSystem,
            status = "uploaded",
            insert_date = datetime.datetime.now(),
            uuid = guid,
            user = get_jwt_identity()
        )
        db.session.add(task)
        db.session.commit()

        send_message(json.dumps({
            "source": PROCESS_ID,
            "action": "RUN_TASK",
            "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "payload": {
              "task_id": task.id,
              "input": sourceFileSystem,
              "output": destinationFileSystem,
              "codec": "mpeg4"
            }
          }), TASKS_QUEUE)
        return {"message": "Task created", "info": task.id} 

class ViewDownloadVideo(Resource):
    # @jwt_required()
    def get(self, uuid, resource):
        # search task within DB
        task_schema = TaskSchema()
        task_db = task_schema.dump(Task.query.filter_by(uuid=uuid).first())

        if not(task_db):
            return {"error": "Task not found"}, 404
        
        # Send the file to download
        if resource == 'origin':
            return send_file(task_db['source_file_system'], as_attachment=True)
        elif resource == 'destination':
            if task_db['status'] != "processed":
                return {"error": "Video processing is not yet processed"}, 400
            return send_file(task_db['destination_file_system'], as_attachment=True)
        else :
            return 'resource invalid', 404 
    