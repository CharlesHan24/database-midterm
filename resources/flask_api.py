
from models.basic_info import *
from models.election import *
from werkzeug.utils import secure_filename
import flask

import threading
sem = threading.Semaphore()


from flask_restful import Resource, reqparse
from flask import send_from_directory, send_file
from flask import after_this_request, request
import json
import pdb
import os

passkey = "qwertyuiop"


class Logout(Resource):
    def get(self):
        return 200

# avoid injection attack
def input_digest(data):
    for key in data.keys():
        data[key].replace("\"", "\\\"")

class Login(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('stuid', type=str, required=True)
    parser.add_argument('password', type=str, required=True)

    def get(self):
        data = Login.parser.parse_args()
        try:
            result = authenticate(data["stuid"], data["password"])
            input_digest(data)

            if result == 401:
                return 401
            else:
                js_ret = {"name": result[4], "contact": str(result[5]), "section": str(result[3]), "position": result[2]}
                return js_ret, 200, [("Set-Cookie", "passkey={}".format(passkey)), ("Set-Cookie", "stu_id={}".format(result[1])), ("Set-Cookie", "position={}".format(result[2])), ("Set-Cookie", "section_id={}".format(result[3]))]
        except:
            return 401


class Candidate_register(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("name", type=str, required=True, location="json")
    parser.add_argument("stuid", type=str, required=True, location="json")
    parser.add_argument("grade", type=str, required=True, location="json")
    parser.add_argument("contact", type=str, required=True, location="json")
    parser.add_argument("application", type=list, required=True, location="json")
    parser.add_argument("brief", type=str, required=True, location="json")
    parser.add_argument("attachment", type=str, required=True, location="json")

    def post(self):
        try:
            data = Candidate_register.parser.parse_args()
            input_digest(data)
            
            result = create_candidate_profile(data["name"], data["stuid"], data["grade"], data["contact"], data["application"], data["brief"], data["attachment"])
            return result

        except:
            return "", 403


class Candidate_upload(Resource):
    def post(self):
        try:
            f = request.files['attachment']
            url = os.path.join("/attach", secure_filename(f.filename))
            f.save(os.getcwd() + url)
            return {"url": url}, 200
        except:
            return "", 403

class Downloads(Resource):
    def get(self, name):
        return send_from_directory(os.getcwd() + "/attach", name, as_attachment=True)

class Candidate_query_list(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("section", type=str)
    parser.add_argument("name", type=str)
    parser.add_argument("page", type=int)
    parser.add_argument("section_id", type=str, required=True, location="cookies")
    parser.add_argument("position", type=str, required=True, location="cookies")
    parser.add_argument("stu_id", type=str, required=True, location="cookies")
    parser.add_argument("passkey", type=str, required=True, location="cookies")

    def get(self):
        try:
            # pdb.set_trace()
            data = Candidate_query_list.parser.parse_args()
            input_digest(data)
            if data["passkey"] != "qwertyuiop":
                return "", 403
            if data["section"] is None:
                data["section"] = -1
            if data["name"] is None:
                data["name"] = "None"
            result = query_cand_list(data, data["section"], data["name"], data["page"])
            if result == 403:
                return "", 403
            else:
                result = result[1]
                resp = []
                for row in result:
                    resp.append({"stuid": str(row[0]), "name": row[1], "grade": str(row[2]), "contact": str(row[3]), "application": [str(x) for x in row[4]], "admitted": [str(x) for x in row[5]], "avg_score": str(row[6]) if row[6] != None else "0"})
                return resp, 200
        except:
            return "", 403

    def delete(self):
        try:
            data = Candidate_query_list.parser.parse_args()
            if data["passkey"] != "qwertyuiop":
                return "", 403
            return clean_all(data)
        except:
            return "", 403


class Candidate_query_info(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("section_id", type=str, required=True, location="cookies")
    parser.add_argument("position", type=str, required=True, location="cookies")
    parser.add_argument("stu_id", type=str, required=True, location="cookies")
    parser.add_argument("passkey", type=str, required=True, location="cookies")

    def get(self, stu_id):
        try:
            # pdb.set_trace()
            data = Candidate_query_info.parser.parse_args()
            input_digest(data)
            if data["passkey"] != "qwertyuiop":
                return "", 403
            result = query_cand_info(data, stu_id)
            if result == 403:
                return "", 403
            elif result == 404:
                return "", 404
            else:
                resp = {"name": result[1], "grade": str(result[2]), "contact": str(result[3]), "application": [str(x) for x in result[4]], "brief": result[5], "attachment": result[6], "admitted": [str(x) for x in result[7]]}
                return resp, 200
        except:
            return "", 403

class Candidate_review(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("score", type=int, required=True, location="json")
    parser.add_argument("text", type=str, required=True, location="json")
    parser.add_argument("section_id", type=str, required=True, location="cookies")
    parser.add_argument("position", type=str, required=True, location="cookies")
    parser.add_argument("stu_id", type=str, required=True, location="cookies")
    parser.add_argument("passkey", type=str, required=True, location="cookies")

    def put(self, stu_id):
        try:
            # pdb.set_trace()
            data = Candidate_review.parser.parse_args()
            input_digest(data)
            if data["passkey"] != "qwertyuiop":
                return "", 403
            result = evaluate(data, stu_id, data["score"], data["text"])
            if result == 403 or result == 404:
                return result
            return {"avg_score": str(result[1])}, result[0]
        except:
            return "", 403


class Candidate_query_review(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("section_id", type=str, required=True, location="cookies")
    parser.add_argument("position", type=str, required=True, location="cookies")
    parser.add_argument("stu_id", type=str, required=True, location="cookies")
    parser.add_argument("passkey", type=str, required=True, location="cookies")

    def get(self, stu_id):
        try:
            # pdb.set_trace()
            data = Candidate_query_review.parser.parse_args()
            input_digest(data)
            if data["passkey"] != "qwertyuiop":
                return "", 403
            result = get_evaluate(data, stu_id)
            if result == 403:
                return "", 403
            elif result == 404:
                return "", 404
            resp = []
            for row in result[1]:
                resp.append({"reviewer": {"stuid": str(row[0]), "name": row[1], "section": str(row[2])}, "reviewTime": row[3], "text": row[4], "score": str(row[5])})
            return resp, 200
        except:
            return "", 403



class Candidate_admit(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("section_id", type=str, required=True, location="cookies")
    parser.add_argument("position", type=str, required=True, location="cookies")
    parser.add_argument("stu_id", type=str, required=True, location="cookies")
    parser.add_argument("passkey", type=str, required=True, location="cookies")

    def put(self, stu_id):
        try:
            
            data = Candidate_admit.parser.parse_args()
            input_digest(data)
            if data["passkey"] != "qwertyuiop":
                return "", 403
            result = admission(data, stu_id)
            if type(result) != tuple:
                return result
            return [str(x) for x in result[1]], 200
        except:
            return "", 403

class Candidate_dismiss(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("section_id", type=str, required=True, location="cookies")
    parser.add_argument("position", type=str, required=True, location="cookies")
    parser.add_argument("stu_id", type=str, required=True, location="cookies")
    parser.add_argument("passkey", type=str, required=True, location="cookies")

    def put(self, stu_id):
        try:
            
            data = Candidate_dismiss.parser.parse_args()
            input_digest(data)
            if data["passkey"] != "qwertyuiop":
                return "", 403
            # pdb.set_trace()
            result = admission_cancel(data, stu_id)
            if type(result) != tuple:
                return result
            return  [str(x) for x in result[1]], 200
        except:
            return "", 403

class Candidate_validate(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("section_id", type=str, required=True, location="cookies")
    parser.add_argument("position", type=str, required=True, location="cookies")
    parser.add_argument("stu_id", type=str, required=True, location="cookies")
    parser.add_argument("passkey", type=str, required=True, location="cookies")

    def get(self):
        try:
            data = Candidate_validate.parser.parse_args()
            if data["passkey"] != "qwertyuiop":
                return "", 403
            result = validate(data)
            if result == 403:
                return "", 403
            return {"validated": result[1]}, 200
        except:
            return "", 403

    def post(self):
        try:
            data = Candidate_validate.parser.parse_args()
            if data["passkey"] != "qwertyuiop":
                return "", 403
            result = admit_finish(data)
            return result
        except:
            return "", 403



class Section_query(Resource):
    def get(self):
        try:
            # pdb.set_trace()
            result, count, heads = query_section()
            resp = []
            for i, row in enumerate(result):
                resp.append({"id": str(row[0]), "name": row[1], "quota": str(row[2]), "memberCount": str(count[i][0][0]), "heads": [{"id": heads[i][j][0], "name": heads[i][j][1]} for j in range(len(heads[i]))]})
            return resp, 200
        except:
            return "", 403





class Section_modify(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("quota", type=int, required=True)
    parser.add_argument("name", type=str, required=True, location="json")
    parser.add_argument("section_id", type=str, required=True, location="cookies")
    parser.add_argument("position", type=str, required=True, location="cookies")
    parser.add_argument("stu_id", type=str, required=True, location="cookies")
    parser.add_argument("passkey", type=str, required=True, location="cookies")

    parser2 = reqparse.RequestParser()
    parser2.add_argument("section_id", type=str, required=True, location="cookies")
    parser2.add_argument("position", type=str, required=True, location="cookies")
    parser2.add_argument("stu_id", type=str, required=True, location="cookies")
    parser2.add_argument("passkey", type=str, required=True, location="cookies")

    def put(self, section_id):
        try:
            data = Section_modify.parser.parse_args()
            input_digest(data)
            if data["passkey"] != "qwertyuiop":
                return "", 403
            result = update_section_name(data, section_id, data["name"])
            if result != 200:
                return result
            result = update_section_limit(data, section_id, data["quota"])
            return result
        except:
            return "", 403

    def delete(self, section_id):
        try:
            data = Section_modify.parser2.parse_args()
            input_digest(data)
            if data["passkey"] != "qwertyuiop":
                return "", 403
            result = delete_section(data, section_id)
            return result
        except:
            return "", 403


class Section_create(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("name", type=str, required=True, location="json")
    parser.add_argument("section_id", type=int, required=True, location="cookies")
    parser.add_argument("position", type=str, required=True, location="cookies")
    parser.add_argument("stu_id", type=str, required=True, location="cookies")
    parser.add_argument("passkey", type=str, required=True, location="cookies")

    def post(self):
        try:
            data = Section_create.parser.parse_args()
            input_digest(data)
            if data["passkey"] != "qwertyuiop":
                return "", 403
            return create_section(data, data["name"])
        except:
            return "", 403

class Member_query(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("section", type=str)
    parser.add_argument("name", type=str)
    parser.add_argument("page", type=int)

    def get(self):
        try:
            # pdb.set_trace()
            data = Member_query.parser.parse_args()
            input_digest(data)
            if data["name"] is None:
                data["name"] = "None"
            if data["section"] is None:
                data["section"] = -1
            result = query_member(data["name"], data["section"], data["page"])
            resp = []
            for row in result:
                resp.append({"id": str(row[0]), "name": row[1], "section": str(row[2]), "position": row[3], "contact": str(row[4])})
            return resp, 200
        except:
            return "", 403


class Member_modify(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("name", type=str, location="json")
    parser.add_argument("section", type=str, location="json")
    parser.add_argument("position", type=str, location="json")
    parser.add_argument("contact", type=str, location="json")
    parser.add_argument("oldPassword", type=str, location="json")
    parser.add_argument("newPassword", type=str, location="json")

    parser2 = reqparse.RequestParser()
    parser2.add_argument("section_id", type=str, required=True, location="cookies")
    parser2.add_argument("position", type=str, required=True, location="cookies")
    parser2.add_argument("stu_id",  type=str, required=True, location="cookies")
    parser2.add_argument("passkey", type=str, required=True, location="cookies")

    def put(self, stu_id):
        try:
            data = Member_modify.parser.parse_args()
            sess = Member_modify.parser2.parse_args()
            input_digest(data)
            input_digest(sess)
            if sess["passkey"] != "qwertyuiop":
                return "", 403
            result = update_member(sess, stu_id, data["name"], data["oldPassword"], data["newPassword"], data["contact"], data["position"], data["section"])
            return result
        except:
            return "", 403

    def delete(self, stu_id):
        try:
            data = Member_modify.parser2.parse_args()
            if data["passkey"] != "qwertyuiop":
                return "", 403
            result = delete_member(data, stu_id)
            return result
        except:
            return "", 403



class Member_create(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("name", type=str, required=True, location="json")
    parser.add_argument("stuid", type=str, required=True, location="json")
    parser.add_argument("section", type=str, required=True, location="json")
    parser.add_argument("position", type=str, required=True, location="json")
    parser.add_argument("contact", type=str, required=True, location="json")
    parser.add_argument("password", type=str, required=True, location="json")

    parser2 = reqparse.RequestParser()
    parser2.add_argument("section_id", type=str, required=True, location="cookies")
    parser2.add_argument("position", type=str, required=True, location="cookies")
    parser2.add_argument("stu_id", type=str, required=True, location="cookies")
    parser2.add_argument("passkey", type=str, required=True, location="cookies")

    def post(self):
        try:
            data = Member_create.parser.parse_args()
            input_digest(data)
            sess = Member_create.parser2.parse_args()
            input_digest(sess)
            if sess["passkey"] != "qwertyuiop":
                return "", 403
            result = add_member(sess, data["stuid"], data["name"], data["password"], data["contact"], data["position"], data["section"])
            return result
        except:
            return "", 403
            

class Candidate_status(Resource):
    def get(self):
        try:
            result = query_reg_enable()
            return {"openRegister": True if result == 1 else False}, 200
        except:
            return "", 403

class Candidate_start(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("section_id", type=str, required=True, location="cookies")
    parser.add_argument("position", type=str, required=True, location="cookies")
    parser.add_argument("stu_id", type=str, required=True, location="cookies")
    parser.add_argument("passkey", type=str, required=True, location="cookies")

    def put(self):
        try:
            data = Candidate_start.parser.parse_args()
            input_digest(data)
            if data["passkey"] != "qwertyuiop":
                return "", 403
            modify_reg_enable(data, 1)
            return 200
        except:
            return "", 403


class Candidate_stop(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("section_id", type=str, required=True, location="cookies")
    parser.add_argument("position", type=str, required=True, location="cookies")
    parser.add_argument("stu_id", type=str, required=True, location="cookies")
    parser.add_argument("passkey", type=str, required=True, location="cookies")

    def put(self):
        try:
            data = Candidate_stop.parser.parse_args()
            input_digest(data)
            if data["passkey"] != "qwertyuiop":
                return "", 403
            modify_reg_enable(data, 0)
            return 200
        except:
            return "", 403


