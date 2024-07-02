from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

from pymongo import MongoClient 

# app = Flask(__name__)

# # Setup the Flask-JWT-Extended extension
# app.config["JWT_SECRET_KEY"] = "secret"
# jwt = JWTManager(app)

# @app.route("/")
# def home():
#   return render_template("home.html")

# @app.route("/login", methods=["POST"])
# def login():
#   username = request.json.get("username", None)
#   password = request.json.get("password", None)
#   if username != "test" or password != "test":
#     return jsonify({"msg": "Bad username or password"}), 401
  
#   access_token = create_access_token(identity=username)
#   return jsonify(access_token=access_token)

# @app.route("/protected", methods=["GET"])
# @jwt_required()
# def protected():
#   current_user = get_jwt_identity()
#   return jsonify(logged_in_as=current_user), 200

# if __name__ == "__main__":
#   app.run()

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbjungle  # 'dbjungle'라는 이름의 db를 만들거나 사용합니다.
users = db.users # 유저 DB

try:
    # MongoDB 클라이언트 설정
    client = MongoClient('localhost', 27017)
    client.server_info()  # 연결이 유효한지 확인
    print("MongoDB 클라이언트 설정 및 연결 확인 완료")

    # 데이터베이스와 컬렉션 선택
    db = client.dbjungle
    users = db.users
    print("데이터베이스와 컬렉션 선택 완료")

    # 모든 사용자 문서 찾기
    all_users = list(users.find({}))
    print("모든 사용자 문서 찾기 완료")

    # 모든 사용자 문서 출력
    print(all_users)
except Exception as e:
    print(f"오류 발생: {e}")