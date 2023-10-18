from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_cors import CORS
from models import db
from views import ViewCreateUser, ViewLogIn
from services import DATABASE_URL


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['JWT_SECRET_KEY'] = 'frase-secreta-app'

app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

cors = CORS(app)

api = Api(app)
api.add_resource(ViewCreateUser, '/api/auth/signup')
api.add_resource(ViewLogIn, '/api/auth/login')

if __name__ == '__main__':
    app.run(debug=True)

jwt = JWTManager(app)