from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient  # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)

app = Flask(__name__)

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.coupang  # 라는 이름의 db를 만들거나 사용합니다.


@app.route('/')
def home():
    return render_template('index2.html')



#데이터 조회
@app.route('/memo', methods=['GET'])
def read_articles():
    # 1. mongoDB에서 _id 값을 제외한 모든 데이터 조회해오기 (Read)
    informations = list(db.informations.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'informations': informations})




#데이터 생성
@app.route('/memo', methods=['POST'])
def post_memo():
    url_receive = request.form['url_give']
    comment_receive = request.form['comment_give']

    # 2. meta tag를 스크래핑하기
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    og_image = soup.select_one('meta[property="og:image"]')
    og_title = soup.select_one('meta[property="og:title"]')
    og_price = soup.select_one('span.total-price > strong')

        # print(og_image)
        # print(og_title)
        # print(og_description)

    price_receive = og_price
    image_receive = og_image['content']
    title_receive = og_title['content']

    # print(og_price)
    # print(url_image)
    # print(url_title)

    informations = {'url':url_receive,
                    'title': title_receive,
                    'price': price_receive,
                    'image': image_receive,
                    'comment':comment_receive}
    # 3. mongoDB에 데이터를 넣기
    db.informations.insert_one(informations)
    return jsonify({'result': 'success'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)
