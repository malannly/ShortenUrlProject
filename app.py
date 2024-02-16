from models_db import *
from wtform_fields import *
from sqlalchemy.exc import IntegrityError
import random, string
#from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, func
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required

def shorten_url():
    while True:
        j = []
        for i in range(4):
            j.append(random.choice(string.ascii_uppercase + string.ascii_lowercase))
            j.append(str(random.randint(0,9)))
        previos = ''.join(j)
        short_url = select([Urls]).filter_by(short = previos).fetchone()
        if not short_url:
            return previos

def rand_strs():
    while True:
        j = []
        for i in range(19):
            j.append(random.choice(string.ascii_uppercase + string.ascii_lowercase))
            j.append(str(random.randint(0,9)))
        previos = ''.join(j)
        rand_srting = select([Check]).filter_by(short = previos).fetchone()
        if not rand_srting:
            return previos
        
app = Flask(__name__)
#db = SQLAlchemy(app)

# building / configurate flask login
login = LoginManager(app)
login.init_app(app)

app.config['SECRET_KEY'] = 'dfghjkjhuisegrhbnkjir'

@login.user_loader
def load_user(id):
    return select([User]).where(User.c.id == int(id)) # hets user's id, has to be an integer

@app.route('/', methods=['POST','GET'])
def home():
    
    reg_form = RegistrationForm()

    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data
        
        hashed_password = pbkdf2_sha256.hash(password) # hash the password

        ip_addr = request.remote_addr
        user = User(username = username, ip_add = ip_addr, password = hashed_password)
        session.add(user)
        session.commit() # adding user
        # user registration was succesful
        
        if user:
            ip_addr = request.remote_addr
            rnd_str = rand_strs()
            reg_check = Check(users = user, ip_add = ip_addr, rand_str = rnd_str)
            session.add(reg_check)
            session.commit()

        flash('Registered successfully. Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('home.html', form = reg_form)
    
@app.route('/login', methods=['POST','GET'])
def login():

    login_form = LoginForm()

    if login_form.validate_on_submit():
        user_object = select([User]).filter_by(username = login_form.username.data).fetchone()
        login_user(user_object, remember = True)
        if current_user.is_authenticated:
            ip_addr = request.remote_addr # gets the ip
            user_check = select([Check]).filter_by(ip_address = ip_addr).fetchone() # checks if there is this ip
            user_name = select([User]).where(User.c.username == login_form.username.data).fetchone()
            user_str = select([Check]).where(Check.c.user_id == user_name.id).fetchone()
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
        #user = User.query.where(User.ip_add == ip_addr).scalar()
        n = 0
        maxi = session.query(func.max(Urls.id)).scalar()
        if maxi == None:
            flash('Shorten url to see your profile.')
            return redirect(url_for('longurl'))
        else:
            url_dict = {}
            url_dict['long_url']=list()
            url_dict['short_url']=list()
            for i in range(maxi):
                n += 1
                url_long = select([Urls.c.long]).where(Urls.c.id == n).scalar() # the name of the link
                url_short = select([Urls.c.short]).where(Urls.c.id == n).scalar() 
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
        user = select([User]).where(User.c.ip_add == ip_addr)
        subscription = session.query(func.count(Premium.user_id)).filter(Premium.user_id == user.id).scalar()
        short_url = shorten_url()
        new_url = Urls(url_recieved, short_url)
            
        #if needs premium
        if subscription <= 4:
            try:
                #shorten url
                session.add(new_url)
                session.commit()

                #relating created shorten url to a user
                sub = Premium(users = user, url = new_url)
                session.add(sub)
                session.commit()
                #task = delete_url.apply_async(url=sub)

            except IntegrityError:
                session.rollback()
                session.add(new_url)
                session.commit()

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
        maxi = session.query(func.max(Urls.id)).scalar()
        url_dict = {}
        url_dict['url']=list()
        url_dict['counts']=list()
        for i in range(maxi):
            n += 1
            url_name =  select([Urls.c.long]).where(Urls.c.id == n).scalar() # the name of the link
            if not url_name in url_dict['url']:
                url_count = session.query(func.count()).filter(Stat.c.urls_id == n).scalar() # count the url
                url_counts = str(url_count)
            url_dict['url'].append(url_name)
            url_dict['counts'].append(url_counts)
        url_dict = zip(url_dict['url'], url_dict['counts']) # groups into tapple

        return render_template('staticsimple.html', url_dict = url_dict)

@app.route('/<short_url>')
def redirection(short_url):
    long_url = session.query(Urls).filter(Urls.c.short == short_url).first()
    adding = Stat(url=long_url)
    if long_url:
        try:
            session.add(adding)
            session.commit()
        except IntegrityError:
            session.rollback()
            session.add(adding)
            session.commit()
            return redirect(long_url.long)
        return redirect(long_url.long)
    else:
        return f'<h2>Ops! This url doesn`t exist</h2>'

if __name__ == '__main__':
    app.run(port=5000,debug=True)