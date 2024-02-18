# -*- coding:utf-8 -*-

import binascii,hashlib,base64,hmac
from urllib import parse


def 编码_UTF8编码(内容: str) -> bytes:
    """
    示例调用:
    - 编码后的内容 = 编码_UTF8编码("测试文本")
    - print(编码后的内容)  # 预期输出: b'\xe6\xb5\x8b\xe8\xaf\x95\xe6\x96\x87\xe6\x9c\xac'
    """
    return 内容.encode('UTF-8', 'strict')

def 编码_UTF8解码(内容: bytes) -> str:
    """
    示例调用:
    - 解码后的内容 = 编码_UTF8解码(b'\xe6\xb5\x8b\xe8\xaf\x95\xe6\x96\x87\xe6\x9c\xac')
    - print(解码后的内容)  # 预期输出: '测试文本'
    """
    return 内容.decode('UTF-8', 'strict')

def 编码_URL编码(内容: str, 不处理字符: str = '') -> str:
    """
    示例调用:
    - 编码后的内容 = 编码_URL编码("测试 文本")
    - print(编码后的内容)  # 预期输出: URL编码后的字符串
    """
    return parse.quote(内容, safe=不处理字符)

def 编码_URL解码(内容: str) -> str:
    """
    示例调用:
    - 解码后的内容 = 编码_URL解码("测试%20文本")
    - print(解码后的内容)  # 预期输出: '测试 文本'
    """
    return parse.unquote(内容)

def 编码_GBK编码(内容: str) -> bytes:
    """
    示例调用:
    - 编码后的内容 = 编码_GBK编码("测试文本")
    - print(编码后的内容)  # 预期输出: GBK编码的字节串
    """
    return 内容.encode('GBK', 'strict')

def 编码_GBK解码(内容: bytes) -> str:
    """
    示例调用:
    - 解码后的内容 = 编码_GBK解码(b'\xce\xca\xbd\xf0\xce\xc4\xbc\xfe')
    - print(解码后的内容)  # 预期输出: '测试文本'
    """
    return 内容.decode('GBK', 'strict')

def 编码_ANSI到USC2(内容: str) -> str:
    """
    示例调用:
    - 转换后的内容 = 编码_ANSI到USC2("测试文本")
    - print(转换后的内容)  # 预期输出: '\\u6d4b\\u8bd5\\u6587\\u672c'
    """
    return ascii(内容)

def 编码_USC2到ANSI(内容: str) -> str:
    """
    示例调用:
    - 转换后的内容 = 编码_USC2到ANSI("\\u6d4b\\u8bd5\\u6587\\u672c")
    - print(转换后的内容)  # 预期输出: '测试文本'
    """
    return 内容.encode('utf-8').decode('unicode_escape')

def 编码_BASE64编码(内容: str) -> str:
    """
    示例调用:
    - 编码后的内容 = 编码_BASE64编码("测试文本")
    - print(编码后的内容)  # 预期输出: Base64编码的字符串
    """
    if isinstance(内容, str):
        内容 = 内容.encode('UTF-8')
    return base64.b64encode(内容).decode('UTF-8')

def 编码_BASE64解码(内容: str, 返回字节集: bool = False) -> str:
    """
    示例调用:
    - 解码后的内容 = 编码_BASE64解码("编码后的Base64字符串", 返回字节集=False)
    - print(解码后的内容)  # 预期输出: 解码后的原始字符串
    """
    解码内容 = base64.b64decode(内容)
    if 返回字节集:
        return 解码内容
    else:
        return 解码内容.decode('UTF-8')

def 加密_MD5(内容: str, 编码: str = "utf-8") -> str:
    """
    计算字符串的MD5散列值。

    :param 内容: 需要计算MD5的字符串。
    :param 编码: 字符串的编码格式，默认为"utf-8"。
    :return: MD5散列值。

    示例调用:
    - md5值 = 加密_MD5("测试文本")
    - print(md5值)  # 预期输出: 字符串的MD5散列值
    """
    MD5 = hashlib.md5()
    MD5.update(内容.encode(encoding=编码))
    return MD5.hexdigest()

def 加密_SHA(内容: str, 类型: int = 2) -> str:
    """
    多种SHA加密算法。

    :param 内容: 需要加密的内容。
    :param 类型: 加密类型，0为SHA1，1为SHA224，2为SHA256，3为SHA384，4为SHA512。
    :return: 加密后的散列值。

    示例调用:
    - sha值 = 加密_SHA("测试文本", 2)
    - print(sha值)  # 预期输出: SHA256散列值
    """
    sha_functions = [hashlib.sha1, hashlib.sha224, hashlib.sha256, hashlib.sha384, hashlib.sha512]
    hash_obj = sha_functions[类型](内容.encode('utf-8'))
    return hash_obj.hexdigest()

def 加密_SHA3(内容: str, 方式: int = 0) -> str:
    """
    使用SHA3算法进行加密。

    :param 内容: 需要加密的内容。
    :param 方式: 加密方式，0为SHA3-224，1为SHA3-256，2为SHA3-384，3为SHA3-512。
    :return: 加密后的散列值。

    示例调用:
    - sha3值 = 加密_SHA3("测试文本", 1)
    - print(sha3值)  # 预期输出: SHA3-256散列值
    """
    sha3_functions = {
        0: hashlib.sha3_224(),
        1: hashlib.sha3_256(),
        2: hashlib.sha3_384(),
        3: hashlib.sha3_512()
    }
    sha3_functions[方式].update(内容.encode('utf-8'))
    return sha3_functions[方式].hexdigest()

# XOR加密作为AES加密的一个简化示例（不推荐用于实际安全需求）
def 加密_XOR(内容: str, 密钥: str) -> str:
    加密内容 = ''.join(chr(ord(c) ^ ord(密钥[i % len(密钥)])) for i, c in enumerate(内容))
    return 加密内容

def 解密_XOR(加密内容: str, 密钥: str) -> str:
    解密内容 = ''.join(chr(ord(c) ^ ord(密钥[i % len(密钥)])) for i, c in enumerate(加密内容))
    return 解密内容

def 加密_HmacSHA256(key: str, 内容: str) -> str:
    """
    使用HMAC和SHA256算法进行加密。

    :param key: 加密密钥。
    :param 内容: 需要加密的内容。
    :return: 加密后的字符串（Base64编码）。

    示例调用:
    - 加密结果 = 加密_HmacSHA256("密钥", "测试文本")
    - print(加密结果)  # 预期输出: HMAC SHA256加密后的Base64字符串
    """
    return base64.b64encode(hmac.new(key.encode('utf-8'), 内容.encode('utf-8'), digestmod=hashlib.sha256).digest()).decode("utf-8")

def 加密_CRC32(内容: str) -> int:
    """
    使用CRC32算法进行加密。

    :param 内容: 需要加密的内容。
    :return: 加密后的整数值。

    示例调用:
    - crc32值 = 加密_CRC32("测试文本")
    - print(crc32值)  # 预期输出: CRC32加密后的整数值
    """
    return binascii.crc32(内容.encode("utf-8"))

def 进制_二到八(内容: str) -> str:
    """
    示例调用:
    - 二进制内容 = '1010'
    - 八进制内容 = 进制_二到八(二进制内容)
    - print(八进制内容)  # 预期输出: '0o12'
    """
    return oct(int(内容, 2))

def 进制_二到十(内容: str) -> int:
    """
    示例调用:
    - 二进制内容 = '1010'
    - 十进制内容 = 进制_二到十(二进制内容)
    - print(十进制内容)  # 预期输出: 10
    """
    return int(内容, 2)

def 进制_二到十六(内容: str) -> str:
    """
    示例调用:
    - 二进制内容 = '1010'
    - 十六进制内容 = 进制_二到十六(二进制内容)
    - print(十六进制内容)  # 预期输出: '0xa'
    """
    return hex(int(内容, 2))

def 进制_八到二(内容: str) -> str:
    """
    示例调用:
    - 八进制内容 = '12'
    - 二进制内容 = 进制_八到二(八进制内容)
    - print(二进制内容)  # 预期输出: '0b1010'
    """
    return bin(int(内容, 8))

def 进制_八到十(内容: str) -> int:
    """
    示例调用:
    - 八进制内容 = '12'
    - 十进制内容 = 进制_八到十(八进制内容)
    - print(十进制内容)  # 预期输出: 10
    """
    return int(内容, 8)

def 进制_八到十六(内容: str) -> str:
    """
    示例调用:
    - 八进制内容 = '12'
    - 十六进制内容 = 进制_八到十六(八进制内容)
    - print(十六进制内容)  # 预期输出: '0xa'
    """
    return hex(int(内容, 8))

def 进制_十到二(内容: int) -> str:
    """
    示例调用:
    - 十进制内容 = 10
    - 二进制内容 = 进制_十到二(十进制内容)
    - print(二进制内容)  # 预期输出: '0b1010'
    """
    return bin(内容)

def 进制_十到八(内容: int) -> str:
    """
    示例调用:
    - 十进制内容 = 10
    - 八进制内容 = 进制_十到八(十进制内容)
    - print(八进制内容)  # 预期输出: '0o12'
    """
    return oct(内容)

def 进制_十到十六(内容: int) -> str:
    """
    示例调用:
    - 十进制内容 = 10
    - 十六进制内容 = 进制_十到十六(十进制内容)
    - print(十六进制内容)  # 预期输出: '0xa'
    """
    return hex(内容)

def 进制_十六到二(内容: str) -> str:
    """
    示例调用:
    - 十六进制内容 = 'a'
    - 二进制内容 = 进制_十六到二(十六进制内容)
    - print(二进制内容)  # 预期输出: '0b1010'
    """
    return bin(int(内容, 16))

def 进制_十六到八(内容: str) -> str:
    """
    示例调用:
    - 十六进制内容 = 'a'
    - 八进制内容 = 进制_十六到八(十六进制内容)
    - print(八进制内容)  # 预期输出: '0o12'
    """
    return oct(int(内容, 16))

def 进制_十六到十(内容: str) -> int:
    """
    示例调用:
    - 十六进制内容 = 'a'
    - 十进制内容 = 进制_十六到十(十六进制内容)
    - print(十进制内容)  # 预期输出: 10
    """
    return int(内容, 16)