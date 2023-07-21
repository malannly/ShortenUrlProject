from celery import Celery
from celery.schedules import crontab

#broker='sqla+sqlite:///urlsdb.sqlite'

app = Celery('celery_app', broker='sqla+sqlite:///celerydb.sqlite', include=['tasks'])
app.conf.beat_schedule = {
    'test' : {
        'task' : 'test',
        'schedule' : crontab(minute='*/1'),
},
}