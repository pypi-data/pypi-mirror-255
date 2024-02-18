# -*- coding:utf-8 -*-
import threading

def 启动线程(函数名, 参数=[], 跟随主线程结束=False):
    """
    启动一个新的线程来运行指定的函数。

    :param 函数名: 要在新线程中运行的函数。
    :param 参数: 传递给函数的参数列表。
    :param 跟随主线程结束: 如果为True，主线程结束时此线程也会结束。
    :return: 创建的线程对象。
    """
    线程 = threading.Thread(target=函数名, args=参数, daemon=跟随主线程结束)
    线程.start()
    return 线程

class 互斥锁:
    """
    一个互斥锁类，使用上下文管理器确保锁的正确获取和释放。
    可以使用with语句自动管理锁的状态，防止死锁。
    with 锁:
    # 在这里执行需要同步的操作
    # ...
    # 当离开这个块的时候，锁会自动释放
    """
    def __init__(self):
        self.__互斥锁 = threading.Lock()

    def __enter__(self):
        self.__互斥锁.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__互斥锁.release()

class 递归锁:
    """
    递归锁类，使用上下文管理器确保锁的正确获取和释放。
    可以使用with语句自动管理锁的状态。
    with 锁:
        # 对共享资源的操作
        共享资源 += 1
        # 递归锁允许在同一线程内重入
        with 锁:
            共享资源 += 1
    """
    def __init__(self):
        self.__递归锁 = threading.RLock()

    def __enter__(self):
        self.__递归锁.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__递归锁.release()


class 信号量:
    """
    信号量类，用于限制同时运行的线程数量。
    使用上下文管理器确保信号量的正确获取和释放。
    可以使用with语句自动管理信号量的状态。
    """
    def __init__(self, 数量=1):
        self.__信号量 = threading.BoundedSemaphore(数量)

    def __enter__(self):
        self.__信号量.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__信号量.release()

class 事件锁:
    def __init__(self):
        self.__事件锁 = threading.Event()

    def 通行(self):
        self.__事件锁.set()

    def 堵塞(self):
        self.__事件锁.clear()

    def 等待(self):
        self.__事件锁.wait()


class 线程类:
    '''
    线程管理 = 线程类(同时运行线程数=4, 总线程数=20)
    for i in range(100):  # 尝试启动10个线程
        线程 = 线程管理.启动线程(示例任务, 参数=(f"任务{i + 1}",))
    if 线程 is None:
        print(f"达到总线程数限制，线程{i + 1}未启动")
    '''
    def __init__(self, 同时运行线程数=None, 总线程数=None):
        self.__线程列表 = []
        self.__信号量 = threading.Semaphore(同时运行线程数) if 同时运行线程数 else None
        self.__总线程数 = 总线程数
        self.__已启动线程数 = 0

    def 启动线程(self, 函数名, 参数=[], 跟随主线程结束=False):
        if self.__总线程数 is not None and self.__已启动线程数 >= self.__总线程数:
            return None  # 达到总线程数限制，不再创建新线程

        def 线程任务包装器(*args, **kwargs):
            if self.__信号量:
                with self.__信号量:
                    函数名(*args, **kwargs)
            else:
                函数名(*args, **kwargs)

        线程 = threading.Thread(target=线程任务包装器, args=参数, daemon=跟随主线程结束)
        线程.start()
        self.__线程列表.append(线程)
        self.__已启动线程数 += 1
        return 线程

    def 等待线程结束(self, 最长等待时间=None):
        """
        等待所有启动的线程结束。

        :param 最长等待时间: 每个线程的最长等待时间，如果为None，则无限等待。
        :return: 所有线程结束时返回True。
        """
        for 线程 in self.__线程列表:
            线程.join(timeout=最长等待时间)
        return True

    def 取运行中的线程对象(self):
        """
        获取当前运行中的所有线程对象。

        :return: 当前运行中的线程列表。
        """
        return threading.enumerate()

    def 线程是否在运行(self, 线程对象):
        """
        判断指定的线程是否还在运行。

        :param 线程对象: 要检查的线程。
        :return: 如果线程在运行返回True，否则返回False。
        """
        return 线程对象.is_alive()

    def 取运行的线程数(self):
        """
        返回由该类创建并且仍在运行的线程数量。

        :return: 运行中的线程数量。
        """
        return sum(线程.is_alive() for 线程 in self.__线程列表)





