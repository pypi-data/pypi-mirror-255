# -*- coding: utf-8 -*-
import datetime,time,random,locale



def 时间_取日期_可调整(日期调整: int = 0) -> str:
    """
    根据给定的调整值返回相应的日期。

    :param 日期调整: 日期调整值，正数表示未来的日期，负数表示过去的日期，0表示今天。
    :return: 调整后的日期。
    """
    return str(datetime.date.today() + datetime.timedelta(days=日期调整))

def 时间_取启动时间() -> float:
    """
    返回程序的启动时间，使用高精度计时器。

    :return: 程序启动到当前的时间（秒）。
    """
    return time.perf_counter()

def 时间_取简化星期名称(时间戳 = None) -> str:
    """
    返回本地简化星期名称（如：Mon）。
    示例调用：print(时间_取简化星期名称())
    预期输出：Mon
    """
    时间戳 = float(时间戳) if 时间戳 is not None else time.time()
    return time.strftime('%a', time.localtime(时间戳))

def 时间_取完整星期名称(时间戳 = None) -> str:
    """
    返回本地完整星期名称（如：Monday）。
    示例调用：print(时间_取完整星期名称())
    预期输出：Monday
    """
    时间戳 = float(时间戳) if 时间戳 is not None else time.time()
    return time.strftime('%A', time.localtime(时间戳))

def 时间_取简化月份名称(时间戳 = None) -> str:
    """
    返回本地简化月份名称（如：Jan）。
    示例调用：print(时间_取简化月份名称())
    预期输出：Jan
    """
    时间戳 = float(时间戳) if 时间戳 is not None else time.time()
    return time.strftime('%b', time.localtime(时间戳))

def 时间_取完整月份名称(时间戳 = None) -> str:
    """
    返回本地完整月份名称（如：January）。
    示例调用：print(时间_取完整月份名称())
    预期输出：January
    """
    时间戳 = float(时间戳) if 时间戳 is not None else time.time()
    return time.strftime('%B', time.localtime(时间戳))

def 时间_取时间_国外格式(时间戳 = None) -> str:
    """
    返回本地相应的日期和时间表示（如：Mon Jan  1 12:00:00 2023）。
    示例调用：print(时间_取时间_国外格式())
    预期输出：Mon Jan  1 12:00:00 2023
    """
    时间戳 = float(时间戳) if 时间戳 is not None else time.time()
    return time.strftime('%c', time.localtime(时间戳))

def 时间_取小时24(时间戳 = None) -> str:
    """
    返回一天中的第几个小时（24小时制，如：12）。
    示例调用：print(时间_取小时24())
    预期输出：12
    """
    时间戳 = float(时间戳) if 时间戳 is not None else time.time()
    return time.strftime('%H', time.localtime(时间戳))

def 时间_取小时12(时间戳 = None) -> str:
    """
    返回第几个小时（12小时制，如：01）。
    示例调用：print(时间_取小时12())
    预期输出：01
    """
    时间戳 = float(时间戳) if 时间戳 is not None else time.time()
    return time.strftime('%I', time.localtime(时间戳))

def 时间_取分钟(时间戳 = None) -> str:
    """
    返回分钟数（如：00）。
    示例调用：print(时间_取分钟())
    预期输出：00
    """
    时间戳 = float(时间戳) if 时间戳 is not None else time.time()
    return time.strftime('%M', time.localtime(时间戳))

def 时间_取秒(时间戳 = None) -> str:
    """
    返回秒数（如：01）。
    示例调用：print(时间_取秒())
    预期输出：01
    """
    时间戳 = float(时间戳) if 时间戳 is not None else time.time()
    return time.strftime('%S', time.localtime(时间戳))

def 时间_取本地AM或PM(时间戳 = None) -> str:
    """
    返回本地AM或PM的相应符号（如：AM）。
    示例调用：print(时间_取本地AM或PM())
    预期输出：AM
    """
    时间戳 = float(时间戳) if 时间戳 is not None else time.time()
    return time.strftime('%p', time.localtime(时间戳))

def 时间_取一年中的第几天(时间戳 = None) -> str:
    """
    返回一年中的第几天（如：046）。
    示例调用：print(时间_取一年中的第几天())
    预期输出：046
    """
    时间戳 = float(时间戳) if 时间戳 is not None else time.time()
    return time.strftime('%j', time.localtime(时间戳))

def 时间_取月份(时间戳 = None) -> str:
    """
    返回月份（如：02）。
    示例调用：print(时间_取月份())
    预期输出：02
    """
    时间戳 = float(时间戳) if 时间戳 is not None else time.time()
    return time.strftime('%m', time.localtime(时间戳))

def 时间_取第几星期(时间戳 = None) -> str:
    """
    返回一年中的第几星期数（如：00-53，星期天是一个星期的开始）。
    示例调用：print(时间_取第几星期())
    预期输出：00
    """
    时间戳 = float(时间戳) if 时间戳 is not None else time.time()
    return time.strftime('%U', time.localtime(时间戳))

def 时间_取第几星期_周一(时间戳 = None) -> str:
    """
    和%U基本相同，不同的是%W以星期一为一个星期的开始
    示例调用：print(时间_取第几星期_周一())
    预期输出：00
    """
    时间戳 = float(时间戳) if 时间戳 is not None else time.time()
    return time.strftime('%U', time.localtime(时间戳))

def 时间_取国外日期格式(时间戳 = None) -> str:
    """
    返回本地相应日期（如：01/01/23）。
    示例调用：print(时间_取国外日期格式())
    预期输出：01/01/23
    """
    时间戳 = float(时间戳) if 时间戳 is not None else time.time()
    return time.strftime('%x', time.localtime(时间戳))

def 时间_取时分秒(时间戳 = None) -> str:
    """
    返回本地相应时间（如：12:00:00）。
    示例调用：print(时间_取时分秒())
    预期输出：12:00:00
    """
    时间戳 = float(时间戳) if 时间戳 is not None else time.time()
    return time.strftime('%X', time.localtime(时间戳))

def 时间_取年份(时间戳 = None) -> str:
    """
    返回完整的年份（如：2023）。
    示例调用：print(时间_取年份())
    预期输出：2023
    """
    时间戳 = float(时间戳) if 时间戳 is not None else time.time()
    return time.strftime('%Y', time.localtime(时间戳))

def 时间_取年份_简写(时间戳 = None) -> str:
    """
    返回去掉世纪的年份（如：23）。
    示例调用：print(时间_取年份_简写())
    预期输出：23
    """
    时间戳 = float(时间戳) if 时间戳 is not None else time.time()
    return time.strftime('%y', time.localtime(时间戳))

def 时间_取时区(时间戳 = None) -> str:
    """
    返回时区的名字（如：+0800）。
    示例调用：print(时间_取时区())
    预期输出：+0800
    """
    时间戳 = float(时间戳) if 时间戳 is not None else time.time()
    return time.strftime('%z', time.localtime(时间戳))

def 时间_取日期(时间戳 = None) -> str:
    """
    返回日期（如：12-10）。
    示例调用：print(时间_取日期())
    预期输出：+0800
    """
    时间戳 = float(时间戳) if 时间戳 is not None else time.time()
    return time.strftime('%m-%d', time.localtime(时间戳))

def 时间_取现行时间(格式: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    返回当前时间的字符串表示。

    :param 格式: 时间的格式化字符串，默认为"%Y-%m-%d %H:%M:%S"。
    :return: 格式化后的当前时间字符串。

    示例调用：print(时间_取现行时间())
    预期输出：2023-01-01 12:00:00 （具体输出取决于当前时间）
    """
    return time.strftime(格式, time.localtime())


def 时间_取现行时间戳(是否取十位: bool = False) -> str:
    """
    返回当前时间的时间戳字符串。

    :param 是否取十位: 是否返回10位的时间戳（秒级）。默认为False，返回13位的时间戳（毫秒级）。
    :return: 当前时间的时间戳字符串。
    """
    if 是否取十位:
        return str(round(time.time()))
    else:
        datetime_object = datetime.datetime.now()
        now_timetuple = datetime_object.timetuple()
        now_second = time.mktime(now_timetuple)
        return str(int(now_second * 1000 + datetime_object.microsecond / 1000))


def 时间_取随机时间戳() -> str:
    """
    返回字符串类型的随机时间戳，介于0到1之间的随机浮点数。

    :return: 随机生成的时间戳字符串。
    """
    return str(random.random())

def 时间_时间转时间戳(时间: str, 格式: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    将符合特定格式的时间字符串转换为10位的时间戳（秒级）。

    :param 时间: 时间字符串。
    :param 格式: 时间的格式，默认为"%Y-%m-%d %H:%M:%S"。
    :return: 字符串类型的10位时间戳。

    示例调用：print(时间_时间转时间戳("2023-01-01 12:00:00"))
    预期输出：'1672531200'
    """
    locale.setlocale(locale.LC_ALL, '')
    return str(int(time.mktime(time.strptime(时间, 格式))))

def 时间_时间戳转时间(时间戳, 格式: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    将10位或13位的时间戳转换为格式化的时间字符串。

    :param 时间戳: 可以是10位或13位的字符串或浮点数时间戳。
    :param 格式: 时间的格式，默认为'%Y-%m-%d %H:%M:%S'。
    :return: 格式化的时间字符串。
    """
    时间戳 = float(时间戳)  # 转换为浮点数以处理字符串和浮点数输入
    if 时间戳 >= 1e12:  # 检测是否为13位时间戳
        时间戳 /= 1000  # 转换为秒
    return time.strftime(格式, time.localtime(int(时间戳)))


def 时间_取时间间隔(原时间: str, 对比时间: str) -> int:
    """
    计算两个时间字符串之间的时间差（秒数）。

    :param 原时间: 起始时间字符串，格式应为"%Y-%m-%d %H:%M:%S"。
    :param 对比时间: 结束时间字符串，格式应为"%Y-%m-%d %H:%M:%S"。
    :return: 两个时间之间的差值（秒数），整数型。

    示例调用：print(时间_取时间间隔("2023-01-02 12:00:00", "2023-01-01 12:00:00"))
    预期输出：86400 （表示两个时间相差一天，即24小时*60分钟*60秒）
    """
    return int(time.mktime(time.strptime(原时间, "%Y-%m-%d %H:%M:%S"))) - int(
        time.mktime(time.strptime(对比时间, "%Y-%m-%d %H:%M:%S")))

def 时间_增减(原时间, 增减部分, 增减数值):
    """
    对原始时间进行增加或减少操作。

    :param 原时间: 可以是字符串或datetime对象。
    :param 增减部分: 1-星期, 2-天, 3-小时, 4-分钟, 5-秒, 6-毫秒。
    :param 增减数值: 增加或减少的数值，正数表示增加，负数表示减少。
    :return: 操作后的datetime对象。

    示例调用及预期输出：
    - print(时间_增减("2023-01-01 12:00:00", 2, 5))  # 增加5天
      输出：2023-01-06 12:00:00
    - print(时间_增减(datetime.datetime.now(), 4, -30))  # 减少30分钟
      输出：当前时间减少30分钟后的时间
    """
    时间差映射 = {
        1: datetime.timedelta(weeks=增减数值),
        2: datetime.timedelta(days=增减数值),
        3: datetime.timedelta(hours=增减数值),
        4: datetime.timedelta(minutes=增减数值),
        5: datetime.timedelta(seconds=增减数值),
        6: datetime.timedelta(milliseconds=增减数值)
    }
    时间差 = 时间差映射[增减部分]
    if isinstance(原时间, str):
        locale.setlocale(locale.LC_ALL, '')
        原时间 = datetime.datetime.strptime(原时间, "%Y-%m-%d %H:%M:%S")
    return 原时间 + 时间差


def 时间_文本转时间(时间文本: str, 格式: str = '%Y-%m-%d %H:%M:%S') -> datetime.datetime:
    """
    将字符串格式的时间转换为 datetime 对象。

    :param 时间文本: 字符串形式的时间。
    :param 格式: 时间文本的格式，默认为 '%Y-%m-%d %H:%M:%S'。
    :return: datetime 对象。
    """
    return datetime.datetime.strptime(时间文本, 格式)


def 时间_时间转文本(时间: datetime.datetime, 格式: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    将datetime时间对象转换为指定格式的字符串。

    :param 时间: datetime时间对象。
    :param 格式: 时间的格式化字符串，默认为"%Y-%m-%d %H:%M:%S"。
    :return: 格式化后的时间字符串。
    """
    return 时间.strftime(格式)


def 时间_格式化(原时间, 时间格式: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    将原始时间（可以是字符串或datetime对象）格式化为指定格式的字符串。

    :param 原时间: 原始时间，可以是符合特定格式的字符串或datetime对象。
    :param 时间格式: 目标时间格式的字符串，默认为"%Y-%m-%d %H:%M:%S"。
    :return: 格式化后的时间字符串。
    """
    if isinstance(原时间, str):
        return datetime.datetime.strptime(原时间, "%Y-%m-%d %H:%M:%S").strftime(时间格式)
    else:
        return 原时间.strftime(时间格式)

