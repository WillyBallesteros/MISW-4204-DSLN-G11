import datetime
import os
import uuid
from flask import request, send_from_directory
from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
from . import DESTINATION_FILEPATH, SOURCE_FILEPATH
from models import db, User, UserSchema, Task, TaskSchema
from services import video
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

    # login
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

class ViewTasks(Resource):
    @jwt_required()
    def get(self, id_task):
        task_schema = TaskSchema()
        return task_schema.dump(Task.query.get_or_404(id_task))

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

        if not video.validate_format(sourceType):
            return 'fileName type cannot be support', 400

        #Check destination type
        destinationType = request.json["newFormat"]
        if format is None:
            return 'newFormat cannot be empty', 400

        destinationType = destinationType.upper()

        if sourceType == destinationType:
            return 'newFormat cannot be equal to file format', 400

        if not video.validate_format(destinationType):
            return 'newFormat cannot be support', 400

        sourceFileSystem = os.path.join(SOURCE_FILEPATH, file.filename)
        destinationFileSystem = os.path.join(DESTINATION_FILEPATH, file.filename)

        #Store file
        file.save(sourceFileSystem)

        guid = uuid.uuid4().hex + uuid.uuid4().hex

        #Create task
        task = TaskSchema(
            file_name = filename,
            source_type = sourceType,
            destination_type = destinationType,
            source_file_system = sourceFileSystem,
            destination_file_system = destinationFileSystem,
            status = "uploaded",
            insert_date = datetime.datetime.now(),
            uuid = guid
            #TODO: append user
        )
        db.session.add(task)
        db.session.commit()
        return {"message": "Task created", "info": task.id}

    @jwt_required()
    def delete(self, id_task):
        #Delete task
        busines_schema = TaskSchema()
        task_db = busines_schema.dump(TaskSchema.query.filter_by(id=id_task).first())
        if task_db is None:
            return 'task not found', 404

        db.session.delete(task_db)
        db.session.commit()
        return {"message": "Task deleted"}
class ViewDownloadVideo(Resource):
    # @jwt_required()
    def get(self, task_id):
        # search task within DB
        task = Task.query.get_or_404(task_id)

        # Verify if the video is completed
        if task.status != "completed":
            return {"error": "Video processing is not yet completed"}, 400

        # Send the file to download
        return send_from_directory(task.destination_file_system, task.file_name, as_attachment=True)