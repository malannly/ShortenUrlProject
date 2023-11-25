from celery_app import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

@app.task(name='delete_url')
def delete_url(url):
    db.session.delete(url)
    db.session.commit()