from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import string, random
from wtform_fields import *

app = Flask(__name__)

app.config['SECRET_KEY'] = 'vnoreh42zjn958berng244on63r45vk5486njb'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Urls(db.Model):
    sp_id = db.Column('sp_id', db.Integer, primary_key = True)
    long = db.Column('long', db.String())
    short = db.Column('short', db.String(8))
    def __init__(self, long, short):
        self.long = long
        self.short = short

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class User(db.Model):
    sp_id = db.Column('sp_id', db.Integer, primary_key = True)
    username = db.Column('username', db.String(29), unique = True, nullable = False)
    password = db.Column('password', db.String(15), nullable = False)
    def __init__(self, username, password):
        self.username = username
        self.password = password

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///daycount.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class Daycount(db.Model):
    sp_id = db.Column('sp_id', db.Integer, primary_key = True)
    sun = db.Column('sun', db.String())
    mon = db.Column('mon', db.String())
    tue = db.Column('tue', db.String())
    wed = db.Column('wed', db.String())
    thu = db.Column('thu', db.String())
    fri = db.Column('fri', db.String())
    sat = db.Column('sat', db.String())
    def __init__(self, sun, mon, tue, wed, thu, fri , sat):
        self.sun = sun
        self.mon = mon
        self.tue = tue
        self.wed = wed
        self.thu = thu
        self.fri = fri
        self.sat = sat

@app.before_first_request
def create_table():
    db.create_all()

def shorten_url():
    while True:
        j = []
        for i in range(4):
            j.append(random.choice(string.ascii_uppercase + string.ascii_lowercase))
            j.append(str(random.randint(0,9)))
        previos = ''.join(j)
        short_url = Urls.query.filter_by(short = previos).first()
        if not short_url:
            return previos

@app.route('/static')
def countnumbers():
    if 'numbers' in session:
        session['numbers'] = session.get('numbers') + 1
    else:
        session['numbers'] = 1
    return render_template('static.html')

@app.route('/', methods=['POST','GET'])
def home():
    return render_template('home.html')

@app.route('/longurl', methods=['POST','GET'])
def longurl():
    if request.method == 'POST':
        url_recieved = request.form['nm']
        found_url = Urls.query.filter_by(long = url_recieved).first()
        if found_url:
            return redirect(url_for('display_short_url',url = found_url.short))
        else:
            short_url = shorten_url()
            new_url = Urls(url_recieved, short_url)
            db.session.add(new_url)
            db.session.commit()
            return redirect(url_for('display_short_url',url = short_url))
    else:
        return render_template('longurl.html')

@app.route('/display/<url>')
def display_short_url(url):
    return render_template('shorturl.html', short_url_display = url)

@app.route('/<short_url>')
def redirection(short_url):
    long_url = Urls.query.filter_by(short=short_url).first()
    if long_url:
        countnumbers()
        return redirect(long_url.long)
    else:
        return f'<h2>Ops! This url doesn`t exist</h2>'

if __name__ == '__main__':
    app.run(port=5000,debug=True)
