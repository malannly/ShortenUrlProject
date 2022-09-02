from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, func, Date
import string, random, datetime
from datetime import date, timedelta

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

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///analytics.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class Day(db.Model):
    sp_id = db.Column('sp_id', db.Integer, primary_key = True)
    datte = db.Column('datte', Date, default=date.today())
    counter = db.Column('counter', db.Integer())
    def __init__(self, counter):
        self.counter = counter

class Clicks(db.Model):
    sp_id = db.Column('sp_id', db.Integer, primary_key = True)
    datte = db.Column('datte', Date, default=date.today() - timedelta(1))
    summary = db.Column('summary', db.Integer())
    def __init__(self, summary):
        self.summary = summary

@app.before_first_request
def create_table():
    db.create_all()

def counting():
    day = Day(counter = 1)
    db.session.add(day)
    db.session.commit()

def checking():
    ago = date.today() - timedelta(1)
    noago = Clicks.query.filter_by(datte = ago).first()
    if not noago:
        daying = Day.query.filter_by(datte = ago).first() # check if there were using last day
        if daying:
            chck = Day.query.where(Day.datte == ago).count() # count last day using
            db.session.add(Clicks(summary = chck))
            db.session.commit()

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

@app.route('/', methods=['POST','GET'])
def home():
    checking()
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

@app.route('/static')
def statistic():
    return render_template('static.html')

@app.route('/<short_url>')
def redirection(short_url):
    long_url = Urls.query.filter_by(short=short_url).first()
    if long_url:
        counting()
        return redirect(long_url.long)
    else:
        return f'<h2>Ops! This url doesn`t exist</h2>'

if __name__ == '__main__':
    app.run(port=5000,debug=True)
