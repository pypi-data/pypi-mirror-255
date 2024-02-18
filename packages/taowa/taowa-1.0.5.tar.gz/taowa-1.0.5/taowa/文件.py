# -*- coding: utf-8 -*-
import sys,os,stat,hashlib
from functools import partial


def 文件_取运行目录() -> str:
    """
    获取当前工作目录的路径。

    :return: 当前工作目录的路径字符串。
    """
    return os.getcwd()

def 文件_取临时目录(目录: str = '.') -> str:
    """
    获取临时目录的路径。在打包的应用程序中用于获取资源文件的地址。

    :param 目录: 默认当前目录，可指定其他目录。
    :return: 临时目录的路径字符串。
    """
    return sys._MEIPASS if getattr(sys, "frozen", False) else os.path.abspath(目录)

def 文件_遍历指定路径文件(路径: str = '.') -> list:
    """
    遍历指定路径下的文件和目录。

    :param 路径: 目录路径，默认为当前目录。
    :return: 目录下的文件名和文件夹名列表。
    """
    return os.listdir(路径)

def 文件_遍历指定路径所有子目录(路径: str = '.') -> list:
    """
    遍历指定路径下的所有子目录。

    :param 路径: 要遍历的根目录路径，默认为当前目录。
    :return: 包含三元组(路径, [包含的目录], [包含的文件])的列表。
    """
    return list(os.walk(路径))

def 文件_创建目录(路径: str) -> bool:
    """
    创建单层目录。如果该目录已存在，则抛出异常。

    :param 路径: 要创建的目录路径。
    :return: 创建成功返回True。
    """
    try:
        os.mkdir(路径)
        return True
    except FileExistsError:
        print(f"目录 {路径} 已存在。")
        return False

def 文件_创建多层目录(路径: str) -> bool:
    """
    创建多层目录结构。如果目录已存在，不会抛出异常。

    :param 路径: 要创建的多层目录路径。
    :return: 创建成功返回True。
    """
    try:
        os.makedirs(路径, exist_ok=True)
        return True
    except Exception as e:
        print(f"创建目录 {路径} 失败: {e}")
        return False

def 文件_写到文件(文件名: str, 写入的数据, 模式: int = 0, 编码: str = "utf-8") -> bool:
    """
    将数据写入到文件中。支持文本和二进制写入模式。

    :param 文件名: 要写入数据的文件名。
    :param 写入的数据: 要写入的数据。
    :param 模式: 写入模式，0为文本追加，1为文本覆盖，2为二进制追加，3为二进制覆盖。
    :param 编码: 文件编码，默认为utf-8。仅在文本模式下使用。
    :return: 成功返回True。
    """
    写入模式 = {0: 'a', 1: 'w', 2: 'ab', 3: 'wb'}

    # 确保目录存在
    目录 = os.path.dirname(文件名)
    if 目录 and not os.path.exists(目录):
        os.makedirs(目录)

    # 写入文件
    if 模式 < 2:
        with open(文件名, 写入模式[模式], encoding=编码) as 文件:
            文件.write(写入的数据)
    else:
        with open(文件名, 写入模式[模式], 'wb') as 文件:
            文件.write(写入的数据)

    return True

def 文件_读取文件(文件名: str, 二进制: bool = False, 编码: str = "utf-8", 读取长度: int = -1,**参数):
    """
    从指定文件中读取数据。

    :param 文件名: 要读取的文件名。
    :param 二进制: 是否以二进制模式读取，False表示文本模式，True表示二进制模式。
    :param 编码: 文件编码，默认为utf-8。仅在文本模式下使用。
    :param 读取长度: 要读取的数据长度，-1表示读取全部内容。
    :return: 读取到的数据。
    """
    模式 = 'rb' if 二进制 else 'r'
    打开参数 = {'encoding': 编码} if not 二进制 else {}
    打开参数.update(**参数)
    with open(文件名, 模式, **打开参数) as 文件:
        return 文件.read(读取长度)

def 文件_删除文件(路径: str) -> bool:
    """
    删除指定路径的文件。如果路径是一个目录，则抛出异常。

    :param 路径: 要删除的文件路径。
    :return: 成功删除返回True。
    """
    try:
        os.remove(路径)
        return True
    except IsADirectoryError:
        print(f"删除失败：路径 {路径} 是一个目录，无法删除。")
        return False
    except FileNotFoundError:
        print(f"删除失败：文件 {路径} 不存在。")
        return False

def 文件_删除文件2(路径: str) -> bool:
    """
    删除指定路径的文件。如果路径是一个目录，则抛出异常。

    :param 路径: 要删除的文件路径。
    :return: 成功删除返回True。
    """
    try:
        os.unlink(路径)
        return True
    except IsADirectoryError:
        print(f"删除失败：路径 {路径} 是一个目录，无法删除。")
        return False
    except FileNotFoundError:
        print(f"删除失败：文件 {路径} 不存在。")
        return False

def 文件_删除空目录(路径: str) -> bool:
    """
    删除单层空目录。如果目录非空或删除失败，则返回False。

    :param 路径: 要删除的目录路径。
    :return: 成功删除返回True，否则返回False。
    """
    try:
        os.rmdir(路径)
        return True
    except Exception as e:
        print(f"{sys._getframe().f_code.co_name}|删除目录失败\r\n{traceback.format_exc()}")
        return False

def 文件_删除多层空目录(路径: str) -> bool:
    """
    递归删除多层空目录。从子目录到父目录逐层尝试删除，遇到非空目录则停止。

    :param 路径: 要删除的目录路径。
    :return: 成功删除返回True，遇到非空目录或失败则抛出异常。
    """
    try:
        os.removedirs(路径)
        return True
    except Exception as e:
        print(f"{sys._getframe().f_code.co_name}|删除多层目录失败\r\n{traceback.format_exc()}")
        return False

def 文件_重命名(原文件名: str, 新文件名: str) -> bool:
    """
    重命名文件或文件夹。

    :param 原文件名: 原始的文件或文件夹名称。
    :param 新文件名: 新的文件或文件夹名称。
    :return: 成功返回True。
    """
    os.rename(原文件名, 新文件名)
    return True

def 文件_目录文件名分割(路径: str) -> tuple:
    """
    分割文件路径为目录和文件名。

    :param 路径: 文件的完整路径。
    :return: (目录, 文件名) 的元组。
    """
    return os.path.split(路径)

def 文件_文件扩展名分割(路径: str) -> tuple:
    """
    分割文件路径为文件名和扩展名。

    :param 路径: 文件的完整路径。
    :return: (文件名, 扩展名) 的元组。
    """
    return os.path.splitext(路径)

def 文件_取文件名(路径: str) -> str:
    """
    从文件路径中提取文件名。

    :param 路径: 文件的完整路径。
    :return: 文件名字符串。
    """
    return os.path.basename(路径)

def 文件_取文件目录(路径: str) -> str:
    """
    从文件路径中提取目录路径。

    :param 路径: 文件的完整路径。
    :return: 目录路径字符串。
    """
    return os.path.dirname(路径)

def 文件_更改当前工作目录(路径: str) -> bool:
    """
    更改当前工作目录到指定路径。

    :param 路径: 新的工作目录路径。
    :return: 成功返回True。
    """
    os.chdir(路径)
    return True

def 文件_更改当前进程目录(路径: str) -> bool:
    """
    更改当前进程的根目录到指定路径。这是一个Unix特有的操作，需要管理员权限。

    :param 路径: 新的根目录路径。
    :return: 成功返回True。
    """
    try:
        os.chroot(路径)
        return True
    except PermissionError:
        print(f"权限错误：无法更改进程的根目录到 {路径}")
        return False
    except Exception as e:
        print(f"更改进程根目录时发生错误: {e}")
        return False

def 文件_是否存在(路径: str) -> bool:
    """
    检测指定路径的文件或目录是否存在。

    :param 路径: 要检测的文件或目录的路径。
    :return: 存在返回True，否则返回False。
    """
    return os.access(路径, os.F_OK)

def 文件_是否可读(路径: str) -> bool:
    """
    检测指定路径的文件或目录是否可读。

    :param 路径: 要检测的文件或目录的路径。
    :return: 可读返回True，否则返回False。
    """
    return os.access(路径, os.R_OK)

def 文件_是否可写(路径: str) -> bool:
    """
    检测指定路径的文件或目录是否可写。

    :param 路径: 要检测的文件或目录的路径。
    :return: 可写返回True，否则返回False。
    """
    return os.access(路径, os.W_OK)

def 文件_是否可执行(路径: str) -> bool:
    """
    检测指定路径的文件或目录是否可执行。

    :param 路径: 要检测的文件或目录的路径。
    :return: 可执行返回True，否则返回False。
    """
    return os.access(路径, os.X_OK)

def 文件_是否为绝对路径(路径: str) -> bool:
    """
    判断给定路径是否为绝对路径。

    :param 路径: 要判断的文件或目录的路径。
    :return: 如果路径是绝对路径则返回True，否则返回False。
    """
    return os.path.isabs(路径)

def 文件_是否为目录(路径: str) -> bool:
    """
    判断给定路径是否为目录。

    :param 路径: 要判断的文件或目录的路径。
    :return: 如果路径是目录则返回True，否则返回False。
    """
    return os.path.isdir(路径)

def 文件_是否为文件(路径: str) -> bool:
    """
    判断给定路径是否为文件。

    :param 路径: 要判断的文件或目录的路径。
    :return: 如果路径是文件则返回True，否则返回False。
    """
    return os.path.isfile(路径)

def 文件_是否存在2(路径: str) -> bool:
    """
    判断给定路径是否存在。

    :param 路径: 要判断的文件或目录的路径。
    :return: 如果路径存在则返回True，否则返回False。
    """
    return os.path.exists(路径)

def 文件_取文件大小(路径: str) -> int:
    """
    返回指定文件的大小。

    :param 路径: 文件的路径。
    :return: 文件的大小（字节为单位）。
    """
    return os.path.getsize(路径)

def 文件_获取文件信息(路径: str) -> tuple:
    """
    获取文件的详细信息。

    :param 路径: 文件的路径。
    :return: 文件信息的元组，包括上次访问时间、修改时间和文件大小。
    """
    结果 = os.stat(路径)
    return (结果.st_atime, 结果.st_mtime, 结果.st_size)

def 文件_修改文件时间(路径: str, 时间: tuple) -> bool:
    """
    修改文件的访问时间和修改时间。

    :param 路径: 文件的路径。
    :param 时间: 时间戳元组，格式为(访问时间戳, 修改时间戳)。
    :return: 成功返回True。
    """
    os.utime(路径, 时间)
    return True

def 文件_取最近访问时间(路径: str) -> int:
    """
    获取文件的最后访问时间。

    :param 路径: 文件的路径。
    :return: 最后访问时间的10位时间戳。
    """
    return int(os.path.getatime(路径))

def 文件_取创建时间(路径: str) -> int:
    """
    获取文件的创建时间。

    :param 路径: 文件的路径。
    :return: 文件创建时间的10位时间戳。
    """
    return int(os.path.getctime(路径))

def 文件_取修改时间(路径: str) -> int:
    """
    获取文件的最后修改时间。

    :param 路径: 文件的路径。
    :return: 文件最后修改时间的10位时间戳。
    """
    return int(os.path.getmtime(路径))

def 文件_取文件MD5(路径: str) -> str:
    """
    计算指定文件的MD5哈希值。

    :param 路径: 文件的路径。
    :return: 文件的MD5哈希值（十六进制字符串）。
    """
    with open(路径, mode='rb') as 文件:
        md5_hash = hashlib.md5()
        for 数据块 in iter(partial(文件.read, 128), b''):
            md5_hash.update(数据块)
    return md5_hash.hexdigest()

def 文件_设为只读(路径: str) -> bool:
    """
    将文件或目录设置为只读。

    :param 路径: 文件或目录的路径。
    :return: 成功返回True。
    """
    os.chmod(路径, stat.S_IREAD)
    return True

def 文件_取消只读(路径: str) -> bool:
    """
    取消文件或目录的只读属性。

    :param 路径: 文件或目录的路径。
    :return: 成功返回True。
    """
    os.chmod(路径, stat.S_IWRITE)
    return True

def 文件_设置可执行(路径: str) -> bool:
    """
    将文件或目录设置为可执行。

    :param 路径: 文件或目录的路径。
    :return: 成功返回True。
    """
    os.chmod(路径, stat.S_IEXEC)
    return True

def 文件_允许所有权限(路径: str) -> bool:
    """
    将文件或目录设置为完全权限（可读、可写、可执行）。

    :param 路径: 文件或目录的路径。
    :return: 成功返回True。
    """
    os.chmod(路径, stat.S_IRWXU)
    return True