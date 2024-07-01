from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

# Flask 애플리케이션 생성
app = Flask(__name__)

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

# 애플리케이션 실행
if __name__ == '__main__':
    app.run(debug=True)
