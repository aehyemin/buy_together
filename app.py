from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient  # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbjungle  # 'dbjungle'라는 이름의 db를 만들거나 사용합니다.


@app.route('/')
def home():
    return render_template('index.html')


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

# 세션 데이터를 암호화하기 위한 비밀 키 설정
app.secret_key = 'supersecretkey'

# 가상의 사용자 데이터베이스
users = {}

# 홈 페이지 라우트 정의
@app.route('/')
def home():
    # 세션에 'username'이 있으면 로그인된 사용자로 환영 메시지를 표시
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    # 세션에 'username'이 없으면 로그인되지 않은 상태로 홈 페이지 표시
    return render_template('home.html')

# 로그인 페이지 라우트 정의
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 폼 데이터에서 사용자 이름과 비밀번호 가져오기
        username = request.form['username']
        password = request.form['password']
        # 사용자 데이터베이스에서 사용자 이름으로 사용자 검색
        user = users.get(username)
        
        # 사용자가 존재하고 비밀번호가 일치하면
        if user and check_password_hash(user['password'], password):
            # 세션에 사용자 이름 저장
            session['username'] = username
            # 홈 페이지로 리다이렉션
            return redirect(url_for('home'))
        else:
            # 로그인 실패 시 플래시 메시지 표시
            flash('Invalid username or password')
    
    # 로그인 페이지 템플릿 렌더링
    return render_template('login.html')

# 회원가입 페이지 라우트 정의
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 폼 데이터에서 사용자 이름과 비밀번호 가져오기
        username = request.form['username']
        password = request.form['password']
        
        # 사용자 이름이 이미 존재하면
        if username in users:
            # 사용자 이름 중복 플래시 메시지 표시
            flash('Username already exists')
        else:
            # 비밀번호 해시 생성
            hashed_password = generate_password_hash(password, method='sha256')
            # 사용자 데이터베이스에 사용자 추가
            users[username] = {'password': hashed_password}
            # 회원가입 성공 플래시 메시지 표시
            flash('User registered successfully')
            # 로그인 페이지로 리다이렉션
            return redirect(url_for('login'))
    
    # 회원가입 페이지 템플릿 렌더링
    return render_template('register.html')

# 로그아웃 라우트 정의
@app.route('/logout')
def logout():
    # 세션에서 사용자 이름 제거
    session.pop('username', None)
    # 홈 페이지로 리다이렉션
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)
