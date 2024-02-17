import threading

def deco_interval(sec=3600):
    def inner(fct):
        def wrapper(*args, **kwargs):
            set_interval(fct, sec, args, kwargs)
        return wrapper
    return inner

def set_interval(func, sec, *args, **kwargs):
    def func_wrapper():
        set_interval(func, sec)
        func(*args, **kwargs)
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t
