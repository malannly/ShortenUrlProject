from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, func, Date
import string, random, datetime, json
from datetime import date, timedelta
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Urls(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    long = db.Column('long', db.String())
    short = db.Column('short', db.String(8))
    days = db.relationship('Day', backref='url', uselist=False)
    def __init__(self, long, short):
        self.long = long
        self.short = short

class Day(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    urls_id = db.Column(db.Integer, db.ForeignKey('urls.id'), nullable=False)
    date = db.Column(db.Date, default = date.today())
    urls = db.relationship('Urls')
    def __init__(self, url):
        self.url = url

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

@app.route('/staticshort')
def statisticshort():
    n = 0
    maxi = db.session.query(db.func.max(Urls.id)).scalar()
    url_tuple = ()
    url_list = []
    for i in range(maxi):
        n += 1
        url_name =  db.session.query(Urls.short).where(Urls.id == n).scalar() # the name of the link
        if not url_name in url_tuple:
            url_counts = Day.query.where(Day.urls_id == n).count() # count the url
            names = 'http://127.0.0.1:5000/'+url_name
            url_tuple = (names,url_counts)
            url_list.append(url_tuple)
        url_tuple_final = tuple(url_list)
    headings = ('Name','Counts')
    return render_template('staticshort.html', headings = headings, url_tuple_final = url_tuple_final)

@app.route('/staticlong')
def statisticlong():
    n = 0
    maxi = db.session.query(db.func.max(Urls.id)).scalar()
    url_tuple = ()
    url_list = []
    for i in range(maxi):
        n += 1
        url_name =  db.session.query(Urls.long).where(Urls.id == n).scalar() # the name of the link
        if not url_name in url_tuple:
            url_counts = Day.query.where(Day.urls_id == n).count() # count the url
            url_name = url_name[0:21]+'...'
            url_tuple = (url_name,url_counts)
            url_list.append(url_tuple)
        url_tuple_final = tuple(url_list)
    headings = ('Name','Counts')
    return render_template('staticlong.html', headings = headings, url_tuple_final = url_tuple_final)

@app.route('/staticsimple')
def statisticsimple():
    n = 0
    maxi = db.session.query(db.func.max(Urls.id)).scalar()
    url_dict = {}
    url_dict['url']=list()
    url_dict['counts']=list()
    for i in range(maxi):
        n += 1
        url_name =  db.session.query(Urls.long).where(Urls.id == n).scalar() # the name of the link
        if not url_name in url_dict['url']:
            url_count = Day.query.where(Day.urls_id == n).count() # count the url
            url_counts = str(url_count)
            url_name = url_name[0:21]+'...'
        url_dict['url'].append(url_name)
        url_dict['counts'].append(url_counts)
    url_dict = zip(url_dict['url'], url_dict['counts'])
    return render_template('staticsimple.html', url_dict = url_dict)

@app.route('/<short_url>')
def redirection(short_url):
    long_url = Urls.query.filter_by(short=short_url).first()
    adding = Day(url=long_url)
    if long_url:
        try:
            db.session.add(adding)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            db.session.add(adding)
            db.session.commit()
            return redirect(long_url.long)
        return redirect(long_url.long)
    else:
        return f'<h2>Ops! This url doesn`t exist</h2>'

if __name__ == '__main__':
    app.run(port=5000,debug=True)