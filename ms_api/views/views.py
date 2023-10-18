from flask import request
from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
from models import db, User, UserSchema
from werkzeug.security import generate_password_hash, check_password_hash
from utils import utils



class ViewLogIn(Resource):

    # login
    def post(self):

        busines_schema = UserSchema()

        # Retrieve user and password from request
        userName = request.json["userName"]
        passwd = request.json["passwd"]


        # Retrieve user from database
        user_db = busines_schema.dump(User.query.filter_by(userName=userName).first())

        if not(user_db):
            return {"error": "User not found"}, 404

        # Verify password using Passlib
        if not check_password_hash(user_db['password'], passwd):
            return {"error": "Invalid password"}, 401

        claims = {
            "name": user_db['userName']
        }
        access_token = create_access_token(identity=user_db['id'], additional_claims=claims)
        return {"message": "loing successful", "token": access_token, "id": user_db['id']}
    
class ViewCreateUser(Resource):

    # login
    def post(self):
        # Retrieve user and password from request
        userName = request.json["userName"]
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
        user_db = User.query.filter_by(userName=userName, email=email).first()
        if user_db is not None:
            return {"error": "Invalid user and email, the combination already exists"}, 401

        
        hash = generate_password_hash(passwd1)

        user = User(
            userName = userName,
            password =  hash,
            email= email
        )
        db.session.add(user)
        db.session.commit()
        return {"mensaje": "User created", "info": user.id}


