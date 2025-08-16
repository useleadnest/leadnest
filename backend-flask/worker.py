from rq import Worker, Queue, Connection
from app.tasks import redis_conn
from app import create_app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        with Connection(redis_conn):
            worker = Worker([Queue('default')])
            worker.work()
