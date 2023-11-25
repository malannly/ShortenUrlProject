from celery import Celery
from celery.schedules import crontab

#broker="amqp://user:password@remote.server.com:port//vhost"

app = Celery('celery_app', broker='amqp://guest:guest@31.153.10.14:5672/admin', include=['tasks'])
app.conf.beat_schedule = {
    'delete_url' : {
        'task' : 'delete_url',
        'schedule' : crontab(minute='*/1'),
},
}