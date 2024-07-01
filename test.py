from flask import Flask, render_template
from flask_jwt_extended import *

application = Flask(import_name = __name__)

application.config.update(
  JWT_SECRET_KEY = 'super-secret'
)

jwt = JWTManager(application)

admin_id = "1234"
admin_pw = "qwer"

@application.route("/")
def test_test():
  return render_template('home.html')

@application.route("/login", methods=['POST'])
def login_proc():

  # 클라이언트로부터 요청된 값
  input_data = request.get_json()
  user_id = input_data['id']
  user_pw = input_data['pw']

  # 아이디, 비밀번호가 일치하는 경우
  if(user_id == admin_id and
     user_pw == admin_pw):
    return jsonify(
      result = "success",
      # 검증된 경우, access 토큰 반화
      access_token = create_access_token(identity = user_id,
                                         expires_delta = False)
    )
  else:
    return jsonify(
      result = "Invalid Params!"
    )

if __name__ == "__main__":
  application.run()