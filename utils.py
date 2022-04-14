# create by andy at 2022/4/1
# reference:
import time
from functools import wraps


def logit(times=3):
    def logging_decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            i = 0
            while i < times:
                try:
                    return func(*args, **kwargs)
                except:
                    time.sleep(1)
                    print(func.__name__, "这个函数错误，正在重新第{}次".format(i))
                    i += 1
            return exit("严重错误")
        return wrapped_function

    return logging_decorator


if __name__ == '__main__':
    pass
