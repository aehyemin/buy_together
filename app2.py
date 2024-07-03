from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, make_response, g
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
# 로그인 관련 라이브러리
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import *
import datetime
import jwt
from functools import wraps
from flask.json.provider import JSONProvider

app = Flask(__name__)
app.config['SECRET_KEY'] = '아무거나'

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.coupang  # 라는 이름의 db를 만들거나 사용합니다.

############################################################################
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

@app.route('/')
# @token_required
def start():
    return render_template('index2.html')

@app.route('/home')
@token_required
def home():
    products = db.informations.find({})
    return render_template('index2.html', products=products)

# # 로그인
# @app.route('/login', methods=['GET'])
# def login_get():
#     return render_template('login.html')

# # 회원가입
# @app.route('/register', methods=['GET'])
# def register_get():
#     return render_template('register.html')

@app.route('/submit', methods=['POST'])
def submit():
    # 폼 데이터 처리
    user_input = request.form['user_input']
    processed_data = f'Processed: {user_input}'
    return render_template('index.html', data={'message': processed_data})

@app.route('/product', methods=['POST'])
def submit():
    # 폼 데이터 처리
    url_receive = request.form['url']
    comment_receive = request.form['comment']

    end_receive = request.form['end']
    min_receive = request.form['min']
    max_receive = request.form['max']

    account_receive = request.form['account']

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36', "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3"}
    data = requests.get(url_receive, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    og_image = soup.select_one('meta[property="og:image"]')
    og_title = soup.select_one('meta[property="og:title"]')
    og_price = soup.select_one('span.total-price > strong').get_text()
    
    price_receive = og_price
    image_receive = og_image['content']
    title_receive = og_title['content']
    
    token = request.cookies.get('token')
    data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
    current_user = data['username']
    user_list = [current_user]
    
    informations = {'url':url_receive,
                    'title': title_receive,
                    'price': price_receive,
                    'image': image_receive,
                    'comment':comment_receive,

                    'min': min_receive,
                    'max': max_receive,
                    'end': end_receive,

                    'account': account_receive,
                    'join': user_list,
                    'register': current_user
                    }
    
    # 3. mongoDB에 데이터를 넣기
    db.informations.insert_one(informations)
    return jsonify({'result': 'success'})

    return render_template('index.html', data={'message': processed_data})
###############################################################################

# 앱 실행
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

