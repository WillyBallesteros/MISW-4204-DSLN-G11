import datetime
import json
import os
import uuid
from flask import request, send_file, make_response
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_restful import Resource
from services.queue_service import send_message
from . import DESTINATION_FILEPATH, SOURCE_FILEPATH, BUCKET_NAME
from models import db, User, UserSchema, Task, TaskSchema
from services import PROCESS_ID, TASKS_TOPIC, video_service
from werkzeug.security import generate_password_hash, check_password_hash
from utils import utils, check_exists
from google.cloud import storage
import os

class ViewHealth(Resource):
    # health
    def get(self):
        response = make_response('OK', 200)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

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

        task['origin_download_link']= task['source_file_system']
        task['destination_download_link']= task['destination_file_system']
        return task
    
    @jwt_required()
    def delete(self, task_id):
        #Delete task
        task = Task.query.filter_by(id=task_id).first()
        if task is None:
            return 'task not found', 404

        bucket = task.source_file_system.split('/')[3]
        sourceFileBucket = task.source_file_system.split('/')[4]        
        destinationFileBucket = task.destination_file_system.split('/')[4]

        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket)
        
        source_blob = bucket.blob(sourceFileBucket)
        if source_blob.exists():
            source_blob.delete()
        
        destination_blob = bucket.blob(destinationFileBucket)
        if destination_blob.exists():
            destination_blob.delete()

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
        sourceName = f"{guid}.{sourceType}"
        destinationName = f"{guid}.{destinationType}"

        destinationFileSystem = f"https://storage.googleapis.com/{BUCKET_NAME}/{destinationName}"
        codec = video_service.get_codec(destinationType)

        sourceFileSystem = sourceName
        if check_exists("X-header-database", request.headers.items()) is None:
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(BUCKET_NAME)
            blob = bucket.blob(sourceName)
            blob.upload_from_string(file.read(), content_type=file.content_type)
            blob.make_public()
            sourceFileSystem = blob.public_url
        
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

        if check_exists("X-header-database", request.headers.items()) is None and check_exists("x-header-database-filesystem", request.headers.items()) is None:
            send_message(json.dumps({
                "source": PROCESS_ID,
                "action": "NEW_TASK",
                "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                "payload": {
                "task_id": task.id,
                "input": sourceFileSystem,
                "output": destinationFileSystem,
                "codec": codec
                }
            }), TASKS_TOPIC)
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
    