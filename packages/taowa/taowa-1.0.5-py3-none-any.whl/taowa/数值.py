# -*- coding: utf-8 -*-
import math,random
from decimal import Decimal


def 到数值(数值: float) -> Decimal:
    """
    将浮点数转换为Decimal类型以提高精度。

    :param 数值: 浮点数。
    :return: Decimal类型的数值。
    """
    return Decimal(str(数值))

def 数值_保留位数(数值: float, 位数: int = 2) -> str:
    """
    将数值格式化为字符串，保留指定位数的小数。

    :param 数值: 浮点数。
    :param 位数: 要保留的小数位数。
    :return: 格式化后的字符串。
    """
    return format(数值, '.{}f'.format(位数))

def 数值_取最小数(数值列表: list) -> float:
    """
    从数值列表中找出并返回最小的数值。

    :param 数值列表: 数值的列表。
    :return: 列表中最小的数值。
    """
    return min(数值列表)

def 数值_取最大数(数值列表: list) -> float:
    """
    从数值列表中找出并返回最大的数值。

    :param 数值列表: 数值的列表。
    :return: 列表中最大的数值。
    """
    return max(数值列表)

def 数值_取上入整数(数值: float) -> int:
    """
    将数值向上取整。

    :param 数值: 浮点数。
    :return: 向上取整后的整数。
    """
    return math.ceil(数值)

def 数值_取下入整数(数值: float) -> int:
    """
    将数值向下取整。

    :param 数值: 浮点数。
    :return: 向下取整后的整数。
    """
    return math.floor(数值)

def 数值_四舍五入(数值: float, 保留位数: int = 0) -> float:
    """
    将数值四舍五入到指定位数的小数。

    :param 数值: 浮点数。
    :param 保留位数: 小数点后保留的位数。
    :return: 四舍五入后的数值。
    """
    return round(数值, 保留位数)

def 数值_取绝对值(数值: float) -> float:
    """
    返回数值的绝对值。

    :param 数值: 浮点数。
    :return: 绝对值。
    """
    return abs(数值)

def 数值_求次方(数值: float, 次方数: int) -> float:
    """
    计算数值的指定次方。

    :param 数值: 底数。
    :param 次方数: 指数。
    :return: 次方计算结果。
    """
    return pow(数值, 次方数)

def 数值_是否在范围内(数值: float, 最小值: float, 最大值: float) -> bool:
    """
    判断一个数值是否在指定的范围内。

    :param 数值: 待判断的数值。
    :param 最小值: 范围的最小值。
    :param 最大值: 范围的最大值。
    :return: 如果数值在范围内返回True，否则返回False。
    """
    return 最小值 <= 数值 <= 最大值

def 数值_转换为整数(数值: float) -> int:
    """
    将浮点数转换为整数。

    :param 数值: 浮点数。
    :return: 转换后的整数。
    """
    return int(数值)

def 数值_求和(数值列表: list) -> float:
    """
    计算数值列表的总和。

    :param 数值列表: 包含数值的列表。
    :return: 总和。
    """
    return sum(数值列表)

def 数值_求平均数(数值列表: list) -> float:
    """
    计算数值列表的平均数。

    :param 数值列表: 包含数值的列表。
    :return: 平均数。
    """
    return sum(数值列表) / len(数值列表) if 数值列表 else 0

def 数值_求平方根(数值: float) -> float:
    """
    计算数值的平方根。

    :param 数值: 非负数值。
    :return: 平方根。
    """
    return math.sqrt(数值)

def 数值_取对数(数值: float, 底数: float) -> float:
    """
    计算以指定底数的对数。

    :param 数值: 需要计算对数的数值。
    :param 底数: 对数的底数。
    :return: 对数值。
    """
    return math.log(数值, 底数)

def 数值_取正弦值(角度: float) -> float:
    """
    计算角度的正弦值。

    :param 角度: 角度，以弧度为单位。
    :return: 正弦值。
    """
    return math.sin(角度)

def 数值_取余弦值(角度: float) -> float:
    """
    计算角度的余弦值。

    :param 角度: 角度，以弧度为单位。
    :return: 余弦值。
    """
    return math.cos(角度)

def 数值_取正切值(角度: float) -> float:
    """
    计算角度的正切值。

    :param 角度: 角度，以弧度为单位。
    :return: 正切值。
    """
    return math.tan(角度)

def 数值_弧度转角度(弧度: float) -> float:
    """
    将弧度值转换为角度值。

    :param 弧度: 弧度值。
    :return: 对应的角度值。
    """
    return math.degrees(弧度)

def 数值_角度转弧度(角度: float) -> float:
    """
    将角度值转换为弧度值。

    :param 角度: 角度值。
    :return: 对应的弧度值。
    """
    return math.radians(角度)

def 数值_取指数值(数值: float) -> float:
    """
    计算数值的自然指数值。

    :param 数值: 任意数值。
    :return: e的数值次幂。
    """
    return math.exp(数值)

def 数值_取正弦的逆(数值: float) -> float:
    """
    计算数值的反正弦值。

    :param 数值: -1到1之间的数值。
    :return: 对应的反正弦值（弧度）。
    """
    return math.asin(数值)

def 数值_取余弦的逆(数值: float) -> float:
    """
    计算数值的反余弦值。

    :param 数值: -1到1之间的数值。
    :return: 对应的反余弦值（弧度）。
    """
    return math.acos(数值)

def 数值_取正切的逆(数值: float) -> float:
    """
    计算数值的反正切值。

    :param 数值: 任意数值。
    :return: 对应的反正切值（弧度）。
    """
    return math.atan(数值)

def 数值_取双曲正弦值(数值: float) -> float:
    """
    计算数值的双曲正弦值。

    :param 数值: 任意数值。
    :return: 对应的双曲正弦值。
    """
    return math.sinh(数值)

def 数值_取双曲余弦值(数值: float) -> float:
    """
    计算数值的双曲余弦值。

    :param 数值: 任意数值。
    :return: 对应的双曲余弦值。
    """
    return math.cosh(数值)

def 数值_取双曲正切值(数值: float) -> float:
    """
    计算数值的双曲正切值。

    :param 数值: 任意数值。
    :return: 对应的双曲正切值。
    """
    return math.tanh(数值)

def 数值_求最大公约数(数值1: int, 数值2: int) -> int:
    """
    计算两个整数的最大公约数。

    :param 数值1: 第一个整数。
    :param 数值2: 第二个整数。
    :return: 最大公约数。
    """
    return math.gcd(数值1, 数值2)

def 数值_取余数(被除数: float, 除数: float) -> float:
    """
    计算两个数相除的余数。

    :param 被除数: 被除数。
    :param 除数: 除数。
    :return: 余数。
    """
    return 被除数 % 除数

def 数值_取模(被除数: float, 除数: float) -> float:
    """
    计算两个数相除的模。

    :param 被除数: 被除数。
    :param 除数: 除数。
    :return: 模。
    """
    return math.fmod(被除数, 除数)

def 数值_取平方(数值: float) -> float:
    """
    计算数值的平方。

    :param 数值: 任意数值。
    :return: 平方值。
    """
    return 数值 ** 2

def 数值_取立方(数值: float) -> float:
    """
    计算数值的立方。

    :param 数值: 任意数值。
    :return: 立方值。
    """
    return 数值 ** 3

def 数值_取阶乘(数值: int) -> int:
    """
    计算数值的阶乘。

    :param 数值: 非负整数。
    :return: 阶乘结果。
    """
    return math.factorial(数值)

def 数值_取随机数(最小值: float, 最大值: float) -> float:
    """
    在指定范围内生成一个随机数。

    :param 最小值: 范围的最小值。
    :param 最大值: 范围的最大值。
    :return: 随机数。
    """
    import random
    return random.uniform(最小值, 最大值)

def 数值_是否为素数(数值: int) -> bool:
    """
    判断一个整数是否为素数。

    :param 数值: 待判断的整数。
    :return: 如果是素数返回True，否则返回False。
    """
    if 数值 <= 1:
        return False
    for i in range(2, int(math.sqrt(数值)) + 1):
        if 数值 % i == 0:
            return False
    return True

def 数值_是否为偶数(数值: int) -> bool:
    """
    判断一个整数是否为偶数。

    :param 数值: 整数。
    :return: 如果是偶数返回True，否则返回False。
    """
    return 数值 % 2 == 0

def 数值_是否为奇数(数值: int) -> bool:
    """
    判断一个整数是否为奇数。

    :param 数值: 整数。
    :return: 如果是奇数返回True，否则返回False。
    """
    return 数值 % 2 != 0

def 数值_求和至(数值: int) -> int:
    """
    计算从1加到指定数值的和。

    :param 数值: 正整数。
    :return: 从1加到该数值的和。
    """
    return sum(range(1, 数值 + 1))

def 数值_求积至(数值: int) -> int:
    """
    计算从1乘到指定数值的积。

    :param 数值: 正整数。
    :return: 从1乘到该数值的积。
    """
    产品 = 1
    for i in range(1, 数值 + 1):
        产品 *= i
    return 产品

def 数值_取随机整数(最小值: int, 最大值: int) -> int:
    """
    在指定范围内生成一个随机整数。

    :param 最小值: 范围的最小值。
    :param 最大值: 范围的最大值。
    :return: 随机整数。
    """
    return random.randint(最小值, 最大值)

def 数值_转换为二进制字符串(数值: int) -> str:
    """
    将整数转换为二进制表示的字符串。

    :param 数值: 整数。
    :return: 二进制表示的字符串。
    """
    return bin(数值)

def 数值_转换为十六进制字符串(数值: int) -> str:
    """
    将整数转换为十六进制表示的字符串。

    :param 数值: 整数。
    :return: 十六进制表示的字符串。
    """
    return hex(数值)

def 数值_转换为八进制字符串(数值: int) -> str:
    """
    将整数转换为八进制表示的字符串。

    :param 数值: 整数。
    :return: 八进制表示的字符串。
    """
    return oct(数值)
