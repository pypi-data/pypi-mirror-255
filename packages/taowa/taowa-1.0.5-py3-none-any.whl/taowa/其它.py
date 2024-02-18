# -*- coding: utf-8 -*-
import time,execjs,re,base64,struct,hmac,hashlib
from io import BytesIO, StringIO
from typing import Any
import ctypes,os,sys

_skinh_dll = None
# 这个路径出现中文会报错
# def 皮肤_加载(皮肤文件名: str='guohe',密码: str='',色调:int =1,饱和度:int =1,亮度:int =1):
#     '''
#     :param 皮肤文件名: 模块Skin文件下的文件名,路径不能有中文,这个不知道怎么解决
#     :param 密码:
#     :param 色调: 1-360
#     :param 饱和度:1-255
#     :param 亮度:1-255
#     :return:
#     '''
#     global _skinh_dll
#     路径 = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.abspath(__file__).replace('\\taowa\\其它.py','')
#     _skinh_dll = ctypes.CDLL(路径 + '\\taowa\\Skin\\Skin.dll')
#     _skinh_dll.SkinH_AttachEx.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]
#     _skinh_dll.SkinH_AttachEx.restype = ctypes.c_int
#     皮肤路径 = 路径 + '\\taowa\\Skin\\'+ 皮肤文件名
#     _skinh_dll.SkinH_AttachEx(皮肤路径.encode('utf-8'), 密码.encode('utf8'),色调,饱和度,亮度)



def 皮肤_加载(皮肤: str='guohe',密码: str='',色调:int =1,饱和度:int =1,亮度:int =1):
    '''
    :param 皮肤: 请查看模块目录下Skin里的文件名
    :param 密码:
    :param 色调: 1-360
    :param 饱和度:1-255
    :param 亮度:1-255
    :return:
    '''
    global _skinh_dll
    路径 = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.abspath(__file__).replace('\\taowa\\其它.py', '')
    _skinh_dll = ctypes.CDLL(路径 + '\\taowa\\Skin\\Skin.dll')
    _skinh_dll.SkinH_AttachRes.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_int,ctypes.c_int]
    _skinh_dll.SkinH_AttachRes.restype = ctypes.c_int

    with open(路径+'\\taowa\\Skin\\'+皮肤, 'rb') as a:
        皮肤 = a.read()
    _skinh_dll.SkinH_AttachRes(皮肤, len(皮肤), 密码.encode('utf8'),色调,饱和度,亮度)

def 皮肤_卸载():
    global _skinh_dll
    _skinh_dll.SkinH_Detach.restype = ctypes.c_int
    _skinh_dll.SkinH_Detach()

def 程序_是否调试运行() -> bool:
    """
    检查程序是否从源码运行,如果打包后运行则返回False。
    """
    # 当使用 PyInstaller 打包时，它会创建一个临时文件夹，该文件夹的路径被存储在 _MEIPASS 中
    return not getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

class __IO共用类:

    def 读取(self, 长度: int = -1) -> Any:
        """
        读取指定长度的内容。长度为-1时读取全部内容。

        :param 长度: 要读取的内容长度，-1表示读取全部内容。
        :return: 读取到的内容字符串。
        """
        return self.read(长度)

    def 读取全部(self) -> str:
        """
        读取流中的全部内容。

        :return: 流中的全部内容字符串。
        """
        return self.getvalue()

    def 写入(self, 内容: Any):
        """
        写入内容到流中。

        :param 内容: 要写入的内容字符串。
        """
        self.write(内容)

    def 写入多行(self, 行列表: list):
        """
        写入多行内容到流中。

        :param 行列表: 包含多行内容的列表。
        """
        self.writelines(行列表)

    def 关闭(self):
        """
        关闭流。
        """
        self.close()

    def 刷新(self):
        """
        刷新流的缓冲区。
        """
        self.flush()

    def 移动到(self, 位置: int):
        """
        移动流的读写位置到指定位置。

        :param 位置: 流中的目标位置。
        """
        self.seek(位置)

    def 当前位置(self) -> int:
        """
        返回当前流的读写位置。

        :return: 当前流的位置。
        """
        return self.tell()

    def 调整大小(self, 新大小: int) -> int:
        """
        调整流的大小。

        :param 新大小: 流的新大小。
        :return: 调整后的流的大小。
        """
        return self.truncate(新大小)

    def 读取行(self) -> str:
        """
        读取流中的一行内容。

        :return: 流中的一行内容字符串。
        """
        return self.readline()

    def 读取所有行(self) -> list:
        """
        读取流中的所有行，返回列表。

        :return: 包含流中所有行的列表。
        """
        return self.readlines()

    def 是否关闭(self) -> bool:
        """
        检查流是否已关闭。

        :return: 如果流已关闭则返回True，否则返回False。
        """
        return self.closed

    def 是否可读(self) -> bool:
        """
        检查流是否可读。

        :return: 如果流可读则返回True，否则返回False。
        """
        return self.readable()

    def 是否可写(self) -> bool:
        """
        检查流是否可写。

        :return: 如果流可写则返回True，否则返回False。
        """
        return self.writable()

    def 是否支持随机访问(self) -> bool:
        """
        检查流是否支持随机访问。

        :return: 如果流支持随机访问则返回True，否则返回False。
        """
        return self.seekable()


class IO_二进制(__IO共用类, BytesIO):
    """BytesIO 处理二进制数据的流。"""

    def 写入(self, 内容: bytes):
        """写入二进制内容到流中。"""
        super().写入(内容)

    def 读取(self, 长度: int = -1) -> bytes:
        """读取指定长度的二进制内容。"""
        return super().读取(长度)

class IO_文本(__IO共用类, StringIO):
    """StringIO 处理文本数据的流。"""

    def 写入(self, 内容: str):
        """写入文本内容到流中。"""
        super().写入(内容)

    def 读取(self, 长度: int = -1) -> str:
        """读取指定长度的文本内容。"""
        return super().读取(长度)


class JavaScript执行器:
    def __init__(self, JS代码: str):
        """
        初始化JavaScript执行器。

        :param JS代码: 要执行的JavaScript代码。
        """
        self.js环境 = execjs.compile(JS代码)

    def 运行(self, 方法名: str, *参数) -> any:
        """
        执行JavaScript代码中的指定方法。

        :param 方法名: JavaScript方法的名称。
        :param 参数: 传递给JavaScript方法的参数。
        :return: JavaScript方法的返回值。
        """
        return self.js环境.call(方法名, *参数)


def 调试输出(*args, 颜色=None):
    """
    打印调试输出，可以选择不同的颜色。

    :param args: 要打印的内容。
    :param 颜色: 打印内容的颜色。可选值包括 '红色', '绿色', '黄色', '蓝色', '紫色', '青色', '白色'。
    """
    颜色代码 = {
        '红色': '\033[91m',
        '绿色': '\033[92m',
        '黄色': '\033[93m',
        '蓝色': '\033[94m',
        '紫色': '\033[95m',
        '青色': '\033[96m',
        '白色': '\033[97m'
    }

    颜色前缀 = 颜色代码.get(颜色, '')
    颜色后缀 = '\033[0m' if 颜色 else ''  # 如果指定了颜色，则在末尾重置

    print(颜色前缀, *args, 颜色后缀)


def 程序_延时(秒数: float):
    """
    实现程序的延时。

    :param 秒数: 要延迟的时间，单位为秒。可以是小数。
    """
    time.sleep(秒数)


def 正则_匹配(原文本: str, 匹配规则: str) -> list:
    """
    根据给定的正则表达式匹配规则，在原文本中查找所有匹配项。

    :param 原文本: 要进行匹配的文本。
    :param 匹配规则: 正则表达式匹配规则。
    :return: 匹配到的所有结果的列表。
    """
    return re.findall(匹配规则, 原文本)


def 谷歌身份验证(secret_key: str) -> str:
    """
    基于时间的谷歌身份验证算法，生成动态验证码。

    :param secret_key: 身份验证器中使用的密钥。
    :return: 生成的六位数动态验证码。
    """
    for x in range(5):  # 最多尝试5次补全
        try:
            decode_secret = base64.b32decode(secret_key, True)
            interval_number = int(time.time() // 30)
            message = struct.pack(">Q", interval_number)
            digest = hmac.new(decode_secret, message, hashlib.sha1).digest()
            index = ord(digest[19:20]) % 16
            google_code = (struct.unpack(">I", digest[index:index + 4])[0] & 0x7fffffff) % 1000000
            return "%06d" % google_code
        except Exception as e:
            secret_key += "="  # 尝试补全密钥

    raise ValueError("无法生成有效的谷歌验证码。请检查密钥是否正确。")


def 运行python代码(代码: str, 全局变量: dict = None, 局部变量: dict = None) -> any:
    """
    动态执行python代码字符串并返回表达式的结果。

    :param 代码: 要执行的python代码字符串。
    :param 全局变量: 全局变量字典。
    :param 局部变量: 局部变量字典。
    :return: 执行代码的结果。
    """
    return eval(代码, 全局变量, 局部变量)


def 运行python代码2(代码: str, 全局变量: dict = None, 局部变量: dict = None) -> None:
    """
    动态执行python代码，不返回结果。

    :param 代码: 要执行的python代码字符串。
    :param 全局变量: 全局变量字典。
    :param 局部变量: 局部变量字典。
    """
    exec(代码, 全局变量, 局部变量)