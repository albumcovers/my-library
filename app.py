from flask import Flask, render_template
import json
import requests

app = Flask(__name__)

def getBookJson():
    js = open('books.json', 'r').read().strip()
    return json.loads(js)

def getIsbnData(isbn):
    return json.loads(requests.get(f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}').text)

@app.route('/isbn/<isbn>')
def get_isbn(isbn):
    return getIsbnData(isbn)

@app.route('/confirm/<isbn>')
def confirm_isbn(isbn):
    js = getIsbnData(isbn)

    title = js['items'][0]['volumeInfo']['title']
    author = js['items'][0]['volumeInfo']['authors'][0]
    return render_template('confirm.html', title=title, author=author)

@app.route('/')
def hello_world():
    does_json = False
    if getBookJson() == {}:
        does_json = False
    else:
        does_json = True
    js = getBookJson()
    return render_template('index.html', json=does_json)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
