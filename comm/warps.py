import time
from functools import wraps

def timer_decorator(msg=None):
    def f(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            if msg:
                print(msg)
            print(f"函数 {func.__name__} 运行时间为: {end_time - start_time:.8f} 秒")           
            return result
        return wrapper
    return f


