from flask import Flask, jsonify
import os
import threading
from flask_jwt_extended import JWTManager
from flask_restful import Api



app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'frase-secreta-app'

app_context = app.app_context()
app_context.push()


cors = CORS(app)

api = Api(app)

if __name__ == '__main__':
    app.run(debug=True)

jwt = JWTManager(app)