# pylint:disable=W0613
# pylint:disable=W0621
from functools import wraps as _wraps
import time as _time
import threading as _threading


class _Thread(_threading.Thread):
    def __init__(
        self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None
    ):
        super(_Thread, self).__init__()
        self.func = target
        self.args = args
        self.result = None

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        _threading.Thread.join(self)  # 等待线程执行完毕
        return self.result


def repeat(number_of_times):
    # 多次执行
    def decorate(func):
        @_wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(number_of_times):
                func(*args, **kwargs)

        return wrapper

    return decorate


def debug(func):
    @_wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Debugging {func.__name__} - args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        print("The return value of this function is ", end="")
        print(result)
        return result

    return wrapper


def run_time(func):
    @_wraps(func)
    def wrapper(*args, **kwargs):
        start = _time.time()
        func(*args, **kwargs)  # 函数在这里运行
        end = _time.time()
        cost_time = end - start
        print("func three run time {}s".format(cost_time))

    return wrapper


def condition(condition):
    def decorator(func):
        @_wraps(func)
        def wrapper(*args, **kwargs):
            if condition:
                return func(*args, **kwargs)
            else:
                return None

        return wrapper

    return decorator


def thread(func):
    @_wraps(func)
    def wrapper(*args, **kwargs):
        threads = _Thread(target=func, args=args, kwargs=kwargs)
        threads.start()
        threads.join()
        return threads.get_result()

    return wrapper
