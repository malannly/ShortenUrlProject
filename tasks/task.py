from celery_app import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

@app.task(name='test')
def delete_url(url):
    db.session.delete(url)
    db.session.commit()