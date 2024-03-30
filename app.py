from flask import Flask, render_template, redirect, request
import json
import random, string
import requests

app = Flask(__name__)
authenticated = False
app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
name = 'books'

def jsonWrite(metadata):
    global name
    l = getBookJson()
    l.append(metadata)
    open(f'{name}.json', 'w').write(json.dumps(l))

def getBookJson():
    global name
    js = open(f'{name}.json', 'r').read().strip()
    return json.loads(js)

def isGif(url):
    try:
        response = requests.head(url)
        content_type = response.headers.get("Content-Type", "")
        return content_type.lower().startswith("image/gif")
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return False


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
    image_link = json.loads(requests.get(f'https://api.bookcover.longitood.com/bookcover/{isbn}').text)['url']
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

@app.route('/book/<i>')
def book(i):
    int_ = int(i)
    b = getBookJson()
    metadata = b[int_]
    title = metadata['title']
    author = metadata['author']
    description = metadata['description']
    publish_date = metadata['publish_date']
    image_link = metadata['image_link']
    return render_template('book.html', 
                           title=title,
                           author=author,
                           summary=description,
                           publish_date=publish_date,
                           image_link=image_link,
                           i=i)

@app.get('/delete/<i>')
def delete_book(i):
    global name
    int_ = int(i)
    b = getBookJson()
    del b[int_]
    open(f'{name}.json', 'w').write(json.dumps(b))
    return redirect('/')

@app.route('/')
def hello_world():
    if not authenticated:
        return render_template('login.html')
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

@app.post('/liblog')
def inter():
    global name
    global authenticated
    
    name = request.form['username']
    try:
        open(f'{name}.json', 'r').read()
        name = name
        authenticated = True
        return redirect('/')
    except:
        open(f'{name}.json', 'w').write('[]')
        name = name
        authenticated = True
        return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5026, debug=True)
