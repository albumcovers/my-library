from flask import Flask, render_template, redirect, request
import json
import requests

app = Flask(__name__)

def jsonWrite(metadata):
    l = getBookJson()
    l.append(metadata)
    open('books.json', 'w').write(json.dumps(l))

def getBookJson():
    js = open('books.json', 'r').read().strip()
    return json.loads(js)

def getIsbnData(isbn):
    return json.loads(requests.get(f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}').text)

@app.route('/isbn/<isbn>')
def get_isbn(isbn):
    return getIsbnData(isbn)

@app.post('/book-add')
def add_book_endpoint():
    isbn = request.form['isbn']
    fixed_isbn = isbn.replace('-', '')
    js = getIsbnData(isbn)

    title = js['items'][0]['volumeInfo']['title']
    author = js['items'][0]['volumeInfo']['authors'][0]
    description = js['items'][0]['volumeInfo']['description']
    publish_date = js['items'][0]['volumeInfo']['publishedDate']
    image_link = f'https://covers.openlibrary.org/b/isbn/{fixed_isbn}-L.jpg'
    metadata = {'title': title, 'author': author, 'description': description, 'publish_date': publish_date, 'image_link': image_link}
    jsonWrite(metadata)
    return redirect('/')

@app.route('/confirm/<isbn>')
def confirm_isbn(isbn):
    try:
        js = getIsbnData(isbn)

        title = js['items'][0]['volumeInfo']['title']
        author = js['items'][0]['volumeInfo']['authors'][0]
        return render_template('confirm.html', title=title, author=author, isbn=isbn)
    except Exception as e:
        return render_template('error.html', error='There was an error parsing your book.', exception=e)

@app.route('/')
def hello_world():
    does_json = False
    if getBookJson() == []:
        does_json = False
    else:
        does_json = True
    js = getBookJson()
    return render_template('index.html', json=does_json, books=getBookJson())

@app.route('/add', methods=['post', 'get'])
def add_book():
    if request.method == 'GET':
        return render_template('add.html')
    elif request.method == 'POST':
        isbn = request.form['isbn']
        return redirect(f'/confirm/{isbn}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5026, debug=True)
