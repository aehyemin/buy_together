from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient  # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)

app = Flask(__name__)

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbjungle  # 'dbjungle'라는 이름의 db를 만들거나 사용합니다.


@app.route('/')
def home():
    return render_template('test.html')


@app.route('/product', methods=['POST'])
def post_article():
    # 1. 클라이언트로부터 데이터를 받기
    url_receive = request.form['url_give']  # 클라이언트로부터 url을 받는 부분
    end_receive = request.form['end_give']
    min_receive = request.form['min_give']
    max_receive = request.form['max_give']
    account_receive = request.form['account_give']
    comment_receive = request.form['comment_give']  # 클라이언트로부터 comment를 받는 부분

    # 2. meta tag를 스크래핑하기
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    # data = requests.get(url_receive, headers=headers)
    # soup = BeautifulSoup(data.text, 'html.parser')

    # og_image = soup.select_one('meta[property="og:image"]')
    # og_title = soup.select_one('meta[property="og:title"]')
    # og_description = soup.select_one('meta[property="og:description"]')

    # url_title = og_title['content']
    # url_description = og_description['content']
    # url_image = og_image['content']
    
    # ------
    user_list = []

    products = {'url': url_receive, 
            #    'name': url_title, 'image': url_description, 'price': url_image,
               'end': end_receive, 'min': min_receive, 'max': max_receive, 'account': account_receive, 'comment': comment_receive,
               'join': user_list }

    # 3. mongoDB에 데이터를 넣기
    db.products.insert_one(products)

    return jsonify({'result': 'success'})


@app.route('/product', methods=['GET'])
def read_articles():
    # 1. mongoDB에서 _id 값을 제외한 모든 데이터 조회해오기 (Read)
    result = list(db.products.find({}, {'_id': 0}))
    # 2. articles라는 키 값으로 article 정보 보내주기
    return jsonify({'result': 'success', 'products': result})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)