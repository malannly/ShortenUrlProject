from celery import Celery
from celery.schedules import crontab

#broker='sqla+sqlite:///urlsdb.sqlite'

app = Celery('celery_app', broker='redis://127.0.0.1:6379/0', include=['tasks'])
app.conf.beat_schedule = {
    'delete_url' : {
        'task' : 'delete_url',
        'schedule' : crontab(minute='*/1'),
},
}