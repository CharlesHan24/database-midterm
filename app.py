from flask import Flask
from flask_jwt import JWT
from flask_restful import Api
from models.election import create_all
from resources.flask_api import *
from flask_cors import CORS

import sys
import MySQLdb

app = Flask(__name__)
CORS(app, supports_credentials=True)

api = Api(app)


@app.before_first_request
def create_tables():
    create_all()


api.add_resource(Login, '/login')
api.add_resource(Logout, "/logout")
api.add_resource(Candidate_register, '/candidate')
api.add_resource(Candidate_upload, '/candidate/upload')
api.add_resource(Candidate_query_list, '/candidates')
api.add_resource(Candidate_query_info, '/candidate/<int:stu_id>')
api.add_resource(Candidate_review, '/candidate/<int:stu_id>/review')
api.add_resource(Candidate_query_review, '/candidate/<int:stu_id>/reviews')
api.add_resource(Candidate_admit, '/candidate/<int:stu_id>/admit')
api.add_resource(Candidate_dismiss, '/candidate/<int:stu_id>/dismiss')
api.add_resource(Candidate_validate, '/candidates/validate')
api.add_resource(Section_query, '/sections')
api.add_resource(Section_modify, '/section/<int:section_id>')
api.add_resource(Section_create, '/section')
api.add_resource(Member_query, '/members')
api.add_resource(Member_modify, '/member/<int:stu_id>')
api.add_resource(Member_create, '/member')
api.add_resource(Candidate_status, "/candidate/status")
api.add_resource(Candidate_start, "/candidates/start")
api.add_resource(Candidate_stop, "/candidates/stop")
api.add_resource(Downloads, "/attach/<string:name>")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)

