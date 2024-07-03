from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, make_response, g
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# 로그인 관련 라이브러리
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import *
import datetime
import jwt
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = '아무거나'

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.coupang  # 라는 이름의 db를 만들거나 사용합니다.


#데이터 조회
@app.route('/product', methods=['GET'])
def read_product():
    # 1. mongoDB에서 _id 값을 제외한 모든 데이터 조회해오기 (Read)
    informations = list(db.informations.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'informations': informations})




#데이터 생성
@app.route('/product', methods=['POST'])
def post_product():

    url_receive = request.form['url_give']
    comment_receive = request.form['comment_give']

    end_receive = request.form['end_give']
    min_receive = request.form['min_give']
    max_receive = request.form['max_give']

    account_receive = request.form['account_give']


    # 2. meta tag를 스크래핑하기
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36', "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3"}
    data = requests.get(url_receive, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    og_image = soup.select_one('meta[property="og:image"]')
    og_title = soup.select_one('meta[property="og:title"]')
    og_price = soup.select_one('span.total-price > strong').get_text()
    
    price_receive = og_price
    image_receive = og_image['content']
    title_receive = og_title['content']

    user_list = []

    informations = {'url':url_receive,
                    'title': title_receive,
                    'price': price_receive,
                    'image': image_receive,
                    'comment':comment_receive,

                    'min': min_receive,
                    'max': max_receive,
                    'end': end_receive,

                    'account': account_receive,
                    'join': user_list}
    
    # 3. mongoDB에 데이터를 넣기
    db.informations.insert_one(informations)
    return jsonify({'result': 'success'})


@app.route('/memo', methods=['GET'])
def read_articles():
    # 1. mongoDB에서 _id 값을 제외한 모든 데이터 조회해오기 (Read)
    result = list(db.articles.find({}, {'_id': 0}))
    # 2. articles라는 키 값으로 article 정보 보내주기
    return jsonify({'result': 'success', 'articles': result})


##### 로그인, 회원가입 구현 #####

names = [
    "고태환", "김경은", "김민경", "김민석", "김민호", "김태현", "김성희", "김슬아",
    "박시원", "박인성", "배지훈", "백승우", "서장우", "윤종성", "이동연", "이승민",
    "이재석", "정유정", "정휘건", "진재웅", "최자영", "최재원", "최주혁", "하혜민",
    "황준용", "염종인", "김해강", "박하연", "김예람", "윤민성", "정현우", "지창근",
    "김영후", "김용성", "임채승", "강경임", "최정우", "박건우", "이동희", "김욱현",
    "조형욱", "정재욱", "이승현", "정소연", "김태민", "서현승", "엄윤준"
]

app.secret_key = 'secretkey' # 비밀 키
users = db.users # 유저 DB

# JWT 토큰 확인 데코레이터
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            return redirect(url_for('login_get'))
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            g.current_user = users.find_one({'username': data['username']})
            if not g.current_user:
                flash('유효하지 않은 사용자입니다.')
                return redirect(url_for('login_get'))
        except jwt.InvalidTokenError:
            flash('틀린 토큰입니다.')
            return redirect(url_for('login_get'))
        return f(*args, **kwargs)
    return decorated_function

# 홈
@app.route('/')
@token_required
def start():
    return render_template('login.html')

@app.route('/home')
@token_required
def home():
    return render_template('index.html')

# 로그인
@app.route('/login', methods=['GET'])
def login_get():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    # 폼에서 유저네임, 비밀번호 받기
    username = request.form['username']
    password = request.form['password']

    # db에서 유저 찾기
    user = users.find_one({'username': username})
    
    # 유저가 있고 비밀번호가 맞으면 토큰 생성
    if user and check_password_hash(user['password'], password):
        token = jwt.encode({
            'username': username,
        }, app.config['SECRET_KEY'], algorithm="HS256")
        response = make_response(redirect(url_for('home')))
        response.set_cookie('token', token)
        return response
    else:
        flash('계정 정보가 서버에 없습니다')
        return redirect(url_for('login_get'))

# 회원가입
@app.route('/register', methods=['GET'])
def register_get():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    # 유저가 보낸 정보 받기
    username = request.form['username']
    password = request.form['password']

    if username not in names:
        flash('이름이 잘못되었습니다')
        return redirect(url_for('login_get'))    
    elif users.find_one({'username': username}):
        flash('같은 이름의 사용자가 이미 존재합니다')
        return redirect(url_for('login_get'))
    else:
        # 비밀번호 해싱 후 db에 저장
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        users.insert_one({'username': username, 'password': hashed_password})
        flash('유저 정보를 성공적으로 저장했습니다')
        return redirect(url_for('login_get'))
    
# 로그아웃
@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('login_get')))
    response.delete_cookie('token')
    return response

# 계정정보 리셋
@app.route('/reset')
def reset():
    users.delete_many({})
    return redirect(url_for('login_get'))

# 토큰 검증 (로그아웃 후 뒤로가기 방지)
@app.route('/check_token')
def check_token():
    token = request.cookies.get('token')
    if not token:
        return jsonify({"logged_in": False})
    try:
        jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return jsonify({"logged_in": True})
    except jwt.ExpiredSignatureError:
        return jsonify({"logged_in": False})
    except jwt.InvalidTokenError:
        return jsonify({"logged_in": False})

# 앱 실행
if __name__ == '__main__':
    app.run(debug=True)

