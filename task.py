from celery import shared_task
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

"""CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/1'"""

app = Flask(__name__)
db = SQLAlchemy(app)

@shared_task()
def delete_url(url):
    db.session.delete(url)
    db.session.commit()