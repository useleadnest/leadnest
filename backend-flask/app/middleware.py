import uuid
import time
import logging
from flask import g, request

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def before_request():
    g.req_id = request.headers.get('x-request-id', str(uuid.uuid4()))
    g.start = time.time()


def after_request(response):
    try:
        duration = round((time.time() - getattr(g, 'start', time.time())) * 1000)
        req_id = getattr(g, 'req_id', 'unknown')
        log.info("[%s] %s %s %s %sms", req_id, request.method, request.path, response.status_code, duration)
        response.headers['x-request-id'] = req_id
    except Exception as e:
        log.warning(f"Middleware error: {e}")
    return response
