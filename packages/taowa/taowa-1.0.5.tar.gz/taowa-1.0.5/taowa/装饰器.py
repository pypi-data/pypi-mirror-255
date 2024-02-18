# -*- coding: utf-8 -*-
import typing,sys,traceback,inspect
from functools import wraps

def 异常捕获(错误返回=None):
    def decorator(func):
        # 如果func不是函数，直接返回不装饰
        if not inspect.isfunction(func):
            return func
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                # 在异常信息中包含函数名、错误详情以及调用时的参数
                # 获取传入的参数
                args_str = ", ".join(repr(a) for a in args)
                kwargs_str = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
                # 获取异常信息
                exc_type, exc_value, exc_traceback = sys.exc_info()
                # 使用 traceback 获取完整的堆栈信息
                trace_info = traceback.extract_tb(exc_traceback)
                # 最后一条记录通常是实际发生异常的位置
                last_call = trace_info[-1]
                filename = last_call.filename
                line_number = last_call.lineno
                function_name = last_call.name
                #拼接传入的参数
                if args_str and kwargs_str:
                    data = ','.join([args_str, kwargs_str])
                elif args_str:
                    data = args_str
                else:
                    data = kwargs_str

                print(f"\033[31m运行出错 {func.__name__}({data})\n错误详情 {exc_value}\n错误位置 {filename}:{line_number}\033[0m")

                if 错误返回 is not None:
                    return 错误返回
                else:
                    return_type = typing.get_type_hints(func).get('return')
                    default_values = {
                        # int: 0, #寻找文本等不适用
                        str: '',
                        bool: False,
                        float: 0.0,
                        list: [],
                        dict: {},
                        set: set(),
                        tuple: tuple(),
                        bytes: b'',
                        bytearray: bytearray(),
                        None: None
                    }
                    return default_values.get(return_type, None)
        return wrapper
    return decorator

