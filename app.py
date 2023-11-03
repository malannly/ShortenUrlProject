from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, func, Date
import string, random, datetime, json, socket
from datetime import date, timedelta
from sqlalchemy.exc import IntegrityError
from passlib.hash import pbkdf2_sha256
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from wtform_fields import *
import ipapi

""" a user will have their own profile where they can create their short urls
    they will see the amount of urls created (they have personally created) 
    and how much they can create
    interface like in spotify
"""

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dfghjkjhuisegrhbnkjir'

#app.config["CELERY_BROKER_URL"] = "redis://localhost:6379"

db = SQLAlchemy(app)

# building / configurate flask login
login = LoginManager(app)
login.init_app(app)

# db for url / to shoten url
class Urls(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    long = db.Column('long', db.String())
    short = db.Column('short', db.String(8))
    days = db.relationship('Day', backref='url', uselist=False)
    prem = db.relationship('Premium', backref='urls', uselist=False)
    def __init__(self, long, short):
        self.long = long
        self.short = short

#db to build static / the usage if each url
class Day(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    urls_id = db.Column(db.Integer, db.ForeignKey('urls.id'), nullable=False)
    date = db.Column(db.Date, default = date.today())
    urls = db.relationship('Urls')
    def __init__(self, url):
        self.url = url

#db for a user / to login / register
class User(UserMixin, db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    username = db.Column('username', db.String(25), unique = True, nullable = False)
    password = db.Column('password', db.String(), nullable = False)
    ip_add = db.Column(db.String())
    connections = db.relationship('Connection', backref='users', uselist=False)
    prem = db.relationship('Premium', backref='user', uselist=False)
    def __init__(self, username, password, ip_add):
        self.username = username
        self.password = password
        self.ip_add = ip_add

#db checks when user logs bt ip adress in as cookies files
class Connection(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    ip_add = db.Column(db.String())
    rand_str = db.Column(db.String(), unique = True)
    user = db.relationship('User')
    def __init__(self, users, ip_add, rand_str):
        self.users = users
        self.ip_add = ip_add
        self.rand_str = rand_str

#db to see how much urls does user has
class Premium(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    urls_id = db.Column(db.Integer, db.ForeignKey('urls.id'), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    users = db.relationship('User')
    url = db.relationship('Urls')
    def __init__(self, users, url):
        self.users = users
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
        
def rand_strs():
    while True:
        j = []
        for i in range(19):
            j.append(random.choice(string.ascii_uppercase + string.ascii_lowercase))
            j.append(str(random.randint(0,9)))
        previos = ''.join(j)
        rand_srting = Connection.query.filter_by(rand_str = previos).first()
        if not rand_srting:
            return previos

@login.user_loader
def load_user(id):
    return User.query.get(int(id)) # hets user's id, has to be an integer

@app.route('/', methods=['POST','GET'])
def home():
    
    reg_form = RegistrationForm()

    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data
        
        hashed_password = pbkdf2_sha256.hash(password) # hash the password

        ip_addr = request.remote_addr
        user = User(username = username, ip_add = ip_addr, password = hashed_password)
        db.session.add(user)
        db.session.commit() # adding user
        # user registration was succesful
        
        if user:
            ip_addr = request.remote_addr
            rnd_str = rand_strs()
            reg_check = Connection(users = user, ip_add = ip_addr, rand_str = rnd_str)
            db.session.add(reg_check)
            db.session.commit()

        flash('Registered successfully. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('home.html', form = reg_form)

@app.route('/login', methods=['POST','GET'])
def login():

    login_form = LoginForm()

    if login_form.validate_on_submit():
        user_object = User.query.filter_by(username = login_form.username.data).first()
        login_user(user_object, remember = True)
        if current_user.is_authenticated:
            ip_addr = request.remote_addr # gets the ip
            user_check = Connection.query.filter_by(ip_add = ip_addr).first() # checks if there is this ip
            user_name = User.query.where(User.username == login_form.username.data).first()
            user_str = Connection.query.where(Connection.user_id == user_name.id).first()
            user_str_check = user_check.rand_str
            if user_check:
                return redirect(url_for('profilepage'))
            
            else:
                flash('wrong')
    return render_template('login.html', form = login_form)

@app.route('/logout', methods=['GET'])
def logout():

    logout_user()

    flash('You have logged out successfully', 'success')
    
    return redirect(url_for('login'))

@app.route('/profilepage', methods = ['POST','GET'])
def profilepage():
    if not current_user.is_authenticated:
        flash('Please login.', 'danger')
        return redirect(url_for('login'))
    
    else:
        ip_addr = request.remote_addr
        user = User.query.where(User.ip_add == ip_addr).scalar()
        n = 0
        maxi = db.session.query(db.func.max(Urls.id)).scalar()
        if maxi == None:
            flash('Shorten url to see your profile.')
            return redirect(url_for('longurl'))
        else:
            url_dict = {}
            url_dict['long_url']=list()
            url_dict['short_url']=list()
            for i in range(maxi):
                n += 1
                url_long =  db.session.query(Urls.long).where(Urls.id == n).scalar() # the name of the link
                url_short =  db.session.query(Urls.short).where(Urls.id == n).scalar()
                if not url_long in url_dict['long_url'] and not url_short in url_dict['short_url']:
                    url_dict['long_url'].append(url_long)
                    url_dict['short_url'].append(url_short)
            url_dict = zip(url_dict['long_url'], url_dict['short_url'])
        
    return render_template('profilepage.html', url_dict = url_dict)

@app.route('/longurl', methods=['POST','GET'])
#@login_required
def longurl():
    if request.method == 'POST':
        url_recieved = request.form['nm']

        #recognise user by ip address to check how many links useer has
        ip_addr = request.remote_addr
        user = User.query.where(User.ip_add == ip_addr).scalar()
        subscription = Premium.query.where(Premium.user_id == user.id).count()
        short_url = shorten_url()
        new_url = Urls(url_recieved, short_url)
            
        #if needs premium
        if subscription <= 4:
            try:
                #shorten url
                db.session.add(new_url)
                db.session.commit()

                #relating created shorten url to a user
                sub = Premium(users = user, url = new_url)
                db.session.add(sub)
                db.session.commit()
                #task = delete_url.apply_async(url=sub)

            except IntegrityError:
                db.session.rollback()
                db.session.add(new_url)
                db.session.commit()

            return redirect(url_for('display_short_url',url = short_url))
                
        else:

            flash('You have already 5 urls. Subscribe to shorten more urls.')
            return render_template('longurl.html')
    
    else:

        if not current_user.is_authenticated:
            flash('Please login.', 'danger')
            return redirect(url_for('login'))

    return render_template('longurl.html')
            

@app.route('/display/<url>')
def display_short_url(url):
    return render_template('shorturl.html', short_url_display = url)

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
            url_dict['url'].append(url_name)
            url_dict['counts'].append(url_counts)
        url_dict = zip(url_dict['url'], url_dict['counts']) # groups into tapple

        return render_template('staticsimple.html', url_dict = url_dict)

"""    else:
        if not current_user.is_authenticated:
            flash('Please login.', 'danger')
            return redirect(url_for('login'))"""

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