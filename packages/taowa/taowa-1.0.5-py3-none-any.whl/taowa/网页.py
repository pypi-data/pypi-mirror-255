# -*- coding: utf-8 -*-
import  html,requests,urllib.parse
requests.packages.urllib3.disable_warnings()
from typing import Union

def 网页_取Host(url: str) -> str:
    """
    从给定的URL中提取主机名。

    :param url: 需要提取主机名的URL字符串。
    :return: 提取出的主机名字符串。
    """
    url = url.strip(' ')  # 去除空格
    url = url if url.startswith('http') else 'http://' + url  # 补全Url
    return urllib.parse.urlsplit(url).hostname


def 网页_html字符解析(文本: str) -> str:
    """
    将特殊的HTML字符实体转换回普通字符。将&amp;这类字符转化成&

    :param 文本: 包含HTML字符实体的字符串。
    :return: 转换后的字符串。
    """
    return html.unescape(文本)


def 网页_取外网IP(返回地区: bool = False) -> tuple:
    """
    从多个在线服务中获取外网IP地址，并可选地返回相关的地区信息。

    :param 返回地区: 布尔值，指示是否返回地区信息。
    :return: 如果返回地区为真，则返回一个元组，包含IP和地区信息；否则仅返回IP地址。
    """
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36"}
    requests.packages.urllib3.disable_warnings()

    # 定义用于尝试获取IP的服务URL列表
    服务列表 = [
        {'id':1,"url": "https://ipservice.ws.126.net/locate/api/getLocByIp?callback=bowlder.cb._2", "start": 14, "end": -1},
        {'id':2,"url": "https://api.bilibili.com/x/web-interface/zone?jsonp=jsonp", "start": 0, "end": None}
    ]

    # 遍历服务列表，尝试获取IP和地区信息
    for 服务 in 服务列表:
        源码 = requests.get(服务["url"], verify=False, headers=header)
        结果 = eval(源码.text[服务["start"]:服务["end"]])

        if 服务["id"] == 1:
            if not 返回地区:
                return 结果['result']['ip'],''
            return 结果['result']['ip'], "{} {} {}".format(结果['result']['country'], 结果['result']['province'], 结果['result']['city'])

        if 服务["id"] == 2:
            if not 返回地区:
                return 结果['data']['addr'],''
            return 结果['data']['addr'], "{} {} {}".format(结果['data']['country'], 结果['data']['province'], 结果['data']['city'])
    # 如果所有尝试都失败，则根据返回地区参数返回相应的默认值
    return '', ''



class __网页返回类型:
    def __init__(self):
        self.源码 = ''
        self.字节集 = b'' #返回字节集,如图片,视频等
        self.cookie = {}
        self.协议头 = {}
        self.状态码 = 0
        self.requests = None
        self.json = {}

Union
def __参数处理(url: str, 方式: int = 0, 参数="", cookie={}, 协议头 = {}, 允许重定向: bool = True, 代理地址: str = None, 编码: str = None, 证书验证: bool = False, 上传文件: dict = None, 补全协议头: bool = True, json: dict = {}, 连接超时: int = 15, 读取超时: int = 15) -> dict():
    参数字典 = dict()
    _协议头 = dict()
    _cookie = dict()
    url = url.strip(' ')# 去除空格
    url = url if url.startswith('http') else 'http://' + url # 补全Url
    #协议头处理
    if type(协议头) == str: # 如果是文本则处理为字典格式
        协议头数组 = 协议头.split('\n')
        for x in 协议头数组:
            名称 = x[0:x.find(':')].strip(' ')
            值 = x[x.rfind(名称) + len(名称) + 1:len(x)].strip(' ')
            if 名称 and 值:
                _协议头[名称] = 值
    else:
        _协议头 = 协议头

    if 补全协议头:
        host = urllib.parse.urlsplit(url).hostname
        if not 'Host' in _协议头:
            _协议头['Host'] = host
        if not 'Accept' in _协议头:
            _协议头['Accept'] = '*/*'
        if not 'Content-Type' in _协议头:
            _协议头['Content-Type'] = 'application/x-www-form-urlencoded'
        if not 'User-Agent' in _协议头:
            _协议头['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36'
        if not 'Referer' in _协议头:
            _协议头['Referer'] = url

    #Cookie处理
    if type(cookie) == str:
        cookie数组 = cookie.split(';')
        for x in cookie数组:
            名称 = x[0:x.find("=")].strip(' ')
            值 = x[cookie.rfind(名称) + len(名称) + 1:len(x)].strip(' ')
            if 名称 and 值:
                _cookie[名称] = 值
    else:
        _cookie = cookie
    #参数处理
    参数字典['url'] = url
    参数字典['verify'] = 证书验证
    参数字典['cookies'] = _cookie
    参数字典['headers'] = _协议头
    参数字典['allow_redirects'] = 允许重定向
    if 参数:
        if 方式 == 0:
            参数字典['params'] = 参数
        else:
            参数字典['data'] = 参数
    if json:
        参数字典['json'] = json
    if 上传文件:
        参数字典['files'] = 上传文件
    if 代理地址:
        参数字典['proxies'] = {"http": "http://" + 代理地址, "https": "https://" + 代理地址}
    if 连接超时 and 读取超时:
        参数字典['timeout'] = (连接超时, 读取超时)
    return 参数字典


def 网页_访问(url: str, 方式: int = 0, 参数="", cookie={}, 协议头 = {}, 允许重定向: bool = True, 代理地址: str = None, 编码: str = None, 证书验证: bool = False, 上传文件: dict = None, 补全协议头: bool = True, json: dict = {}, 连接超时: int = 15, 读取超时: int = 15,Class=requests) -> __网页返回类型:
    """
    从给定的URL访问网页，并返回响应内容。

    :param url: 链接,能自动补全http,去除首尾空格
    :param 方式: 请求方式（0.get, 1.post, 2.put, 3.delete, 4.head, 5.options）
    :param 参数: 请求参数（文本或字典）
    :param cookie: 请求cookie（文本或字典）
    :param 协议头: 请求头部信息（文本或字典）
    :param 允许重定向: 是否允许自动重定向
    :param 代理地址: 代理服务器地址 账号:密码@IP:端口  或  IP:端口
    :param 编码: 响应内容的编码方式  utf8,gbk·······
    :param 证书验证: 是否验证HTTPS证书
    :param 上传文件: 上传的文件信息 {'upload': ('code.png', 图片字节集, 'image/png')}
    :param 补全协议头: 是否补全标准协议头
    :param json: JSON格式的参数
    :param 连接超时: 连接超时时间
    :param 读取超时: 读取超时时间
    :return: 返回网页对象
    """
    参数字典 = __参数处理(url, 方式, 参数, cookie, 协议头, 允许重定向, 代理地址, 编码, 证书验证, 上传文件, 补全协议头,json,连接超时, 读取超时)

    网页 = __网页返回类型()
    请求方式映射 = {
        0: Class.get,
        1: Class.post,
        2: Class.put,
        3: Class.delete,
        4: Class.head,
        5: Class.options
    }
    if 方式 in 请求方式映射:
        请求方法 = 请求方式映射[方式]
        try:
            网页对象 = 请求方法(**参数字典)
            if 编码:
                网页对象.encoding = 编码
            网页.requests = 网页对象
            网页.源码 = 网页对象.text
            网页.cookie = dict(网页对象.cookies)
            网页.状态码 = 网页对象.status_code
            网页.协议头 = 网页对象.headers
            网页.字节集 = 网页对象.content
            网页.json = 网页对象.json()
        except Exception as e:
            网页.json = {}
    return 网页


class 网页_会话:
    "自动处理Cookie"

    def __init__(self,重连次数: int = 0):
        """
        初始化网络请求会话，并设置重连次数。

        :param 重连次数: HTTP/HTTPS 请求的最大重试次数。
        """
        self.requests = requests.session()
        if 重连次数:
            self.requests.mount('http://', HTTPAdapter(max_retries=重连次数))
            self.requests.mount('https://', HTTPAdapter(max_retries=重连次数))


    def 访问(self,url: str, 方式: int = 0, 参数="", cookie={}, 协议头={}, 允许重定向: bool = True, 代理地址: str = None, 编码: str = None, 证书验证: bool = False, 上传文件: dict = None, 补全协议头: bool = True, json: dict = {}, 连接超时: int = 15, 读取超时: int = 15):
        """
        从给定的URL访问网页，并返回响应内容。

        :param url: 链接,能自动补全http,去除首尾空格
        :param 方式: 请求方式（0.get, 1.post, 2.put, 3.delete, 4.head, 5.options）
        :param 参数: 请求参数（文本或字典）
        :param cookie: 请求cookie（文本或字典）
        :param 协议头: 请求头部信息（文本或字典）
        :param 允许重定向: 是否允许自动重定向
        :param 代理地址: 代理服务器地址 账号:密码@IP:端口  或  IP:端口
        :param 编码: 响应内容的编码方式  utf8,gbk·······
        :param 证书验证: 是否验证HTTPS证书
        :param 上传文件: 上传的文件信息 {'upload': ('code.png', 图片字节集, 'image/png')}
        :param 补全协议头: 是否补全标准协议头
        :param json: JSON格式的参数
        :param 连接超时: 连接超时时间
        :param 读取超时: 读取超时时间
        :return: 返回网页对象
        """
        return 网页_访问(url, 方式, 参数, cookie, 协议头, 允许重定向, 代理地址, 编码, 证书验证, 上传文件, 补全协议头,json,连接超时, 读取超时,Class=self.requests)