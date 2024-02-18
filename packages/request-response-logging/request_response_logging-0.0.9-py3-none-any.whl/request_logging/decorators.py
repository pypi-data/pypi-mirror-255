import uuid
from functools import wraps

from request_logging.middleware.RequestResponseLogging import ctx_request_id


def generate_request_id(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = None
        try:
            ctx_request_id.get()
        except LookupError:
            token = ctx_request_id.set(kwargs.get('context_var') or uuid.uuid4().hex)
        result = func(*args, **kwargs)
        if token:
            ctx_request_id.reset(token)
        return result

    return wrapper
