# -*- coding: utf-8 -*-
import pkgutil,types,importlib
from .装饰器 import *


def 自动装饰器_应用(包名):
    包 = importlib.import_module(包名)
    for 加载器, 模块名, 是包 in pkgutil.walk_packages(包.__path__, 包.__name__ + '.'):
        if not 是包:
            模块 = importlib.import_module(模块名)
            for 属性名 in dir(模块):
                属性 = getattr(模块, 属性名)
                if isinstance(属性, types.FunctionType):
                    装饰后的函数 = 异常捕获()(属性)
                    setattr(模块, 属性名, 装饰后的函数)

自动装饰器_应用('taowa')


# from .wx界面 import *
# from .以太坊 import *
from .网页 import *
from .编码 import *
from .文本 import *
from .文件 import *
from .系统 import *
from .win32 import *
from .时间 import *
from .线程 import *
from .其它 import *

__version__ = '1.0.5'