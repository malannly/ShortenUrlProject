from settings import db
from flask_login import UserMixin
from sqlalchemy import DateTime, func, Date
from datetime import date, timedelta
import string, random, datetime, json, socket

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
