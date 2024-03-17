import create_eng
from datetime import date, timedelta, datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, DateTime

engine = create_engine("sqlite:///urluser.db")
conn = engine.connect()
# object which is used to store information about the database schema
metadata = MetaData()

#urls db
Urls = Table('Urls',metadata,
            Column('id', Integer(), primary_key=True),
            Column('long', String()),
            Column('short', String(8))
            )

#user db
User = Table('User', metadata,
            Column('id', Integer(), primary_key=True),
            Column('username', String(25)),
            Column('password', String())
            )

#static db
Stat = Table('Stat', metadata,
            Column('id', Integer(), primary_key=True),
            Column('urls_id', Integer(), ForeignKey('Urls.id')),
            Column('date', DateTime, default = date.today())
             )

#checking user's identity
Check = Table('Check', metadata,
              Column('id', Integer(), primary_key=True),
              Column('user_id', Integer(), ForeignKey('User.id')),
              Column('ip_address', String()),
              Column('random_str', String(), unique=True)
              )

#for premium users
Premium = Table('Premium', metadata,
              Column('id', Integer(), primary_key=True),
              Column('user_id', Integer(), ForeignKey('User.id')),
              Column('urls_id', String(), ForeignKey('Urls.id')),
              Column('date', DateTime, default = date.today())
              )

metadata.create_all(engine)