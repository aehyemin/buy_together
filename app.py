from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, make_response
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient  # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)

# 로그인 관련 라이브러리
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import *
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = '아무거나'

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbjungle  # 'dbjungle'라는 이름의 db를 만들거나 사용합니다.


@app.route('/memo', methods=['POST'])
def post_article():
    # 1. 클라이언트로부터 데이터를 받기
    url_receive = request.form['url_give']  # 클라이언트로부터 url을 받는 부분
    comment_receive = request.form['comment_give']  # 클라이언트로부터 comment를 받는 부분

    # 2. meta tag를 스크래핑하기
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    og_image = soup.select_one('meta[property="og:image"]')
    og_title = soup.select_one('meta[property="og:title"]')
    og_description = soup.select_one('meta[property="og:description"]')

    url_title = og_title['content']
    url_description = og_description['content']
    url_image = og_image['content']

    article = {'url': url_receive, 'title': url_title, 'desc': url_description, 'image': url_image,
               'comment': comment_receive}

    # 3. mongoDB에 데이터를 넣기
    db.articles.insert_one(article)

    return jsonify({'result': 'success'})


@app.route('/memo', methods=['GET'])
def read_articles():
    # 1. mongoDB에서 _id 값을 제외한 모든 데이터 조회해오기 (Read)
    result = list(db.articles.find({}, {'_id': 0}))
    # 2. articles라는 키 값으로 article 정보 보내주기
    return jsonify({'result': 'success', 'articles': result})


##### 로그인, 회원가입 구현 #####

app.secret_key = 'secretkey' # 비밀 키
users = db.users # 유저 DB

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            flash('토큰이 없습니다')
            return redirect(url_for('login_get'))
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = users.find_one({'username': data['username']})
        except:
            flash('틀린 토큰입니다')
            return redirect(url_for('login_get'))
        return f(current_user, *args, **kwargs)
    return decorated

# 홈
@app.route('/')
@token_required # 토큰이 있는지 (로그인 돼있는지 확인)
def start():
    return render_template('index.html')

# @app.route('/index')
# @token_required
# def index(current_user):
#     return render_template('index.html', username=current_user['username'])

# 로그인
@app.route('/login', methods=['GET'])
def login_get():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    user = users.find_one({'username': username})
    
    if user and check_password_hash(user['password'], password):
        token = jwt.encode({
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        response = make_response(redirect(url_for('index')))
        response.set_cookie('token', token)
        return response
    else:
        flash('Invalid username or password')

# 회원가입
@app.route('/register', methods=['GET'])
def register_get():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    username = request.form['username']
    password = request.form['password']
    
    if users.find_one({'username': username}):
        flash('Username already exists')
    else:
        hashed_password = generate_password_hash(password, method='sha256')
        users.insert_one({'username': username, 'password': hashed_password})
        flash('User registered successfully')
        return redirect(url_for('login'))
    
# 로그아웃
@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('token')
    return response

# 앱 실행
if __name__ == '__main__':
    app.run(debug=True)