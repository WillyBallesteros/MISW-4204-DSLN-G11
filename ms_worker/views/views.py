from flask import make_response
from flask_restful import Resource

class ViewHealth(Resource):
    # health
    def get(self):
        response = make_response('OK', 200)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response