from functools import wraps


def lazy_call(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        def inner_call(**late_kwargs):
            complete_kwargs = {**kwargs, **late_kwargs}
            return f(*args, **complete_kwargs)
        return inner_call
    return wrapper
