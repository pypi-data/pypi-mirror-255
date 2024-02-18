# -*- coding: utf-8 -*-
import socket,subprocess,winreg,ctypes,os,sys,re,uuid,signal


def 系统_取本机电脑名称() -> str:
    """
    获取本机电脑的名称。

    :return: 返回电脑的名称。如果发生异常，则返回空。
    """
    return socket.gethostname()


def 系统_执行Dos(命令: str) -> bool:
    """
    使用subprocess执行给定的DOS命令。

    :param 命令: 要执行的命令行命令。
    :return: 命令执行成功返回True，失败返回False。
    """
    try:
        result = subprocess.run(命令, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def 系统_执行Dos_带返回(命令: str) -> str:
    """
    使用subprocess执行给定的DOS命令，并返回命令的输出结果。

    :param 命令: 要执行的命令行命令。
    :return: 返回命令的标准输出结果。
    """
    with subprocess.Popen(命令, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
        stdout, stderr = p.communicate()
        if p.returncode == 0:
            return stdout.decode('utf-8')
        else:
            return stderr.decode('utf-8')


def 系统_执行Dos_os(命令: str) -> bool:
    """
    使用os.system执行给定的DOS命令。

    :param 命令: 要执行的命令行命令。
    :return: 命令执行成功返回True，失败返回False。
    """
    状态码 = os.system(命令)
    return 状态码 == 0


def 系统_执行Dos_带返回_os(命令: str) -> str:
    """
    使用os.popen执行给定的DOS命令，并返回命令的输出结果。

    :param 命令: 要执行的命令行命令。
    :return: 返回命令的标准输出结果。
    """
    with os.popen(命令) as f:
        结果 = f.read()
    return 结果


def 系统_连接宽带(宽带名称: str, 用户名: str, 密码: str) -> bool:
    """
    尝试使用指定的用户名和密码连接到宽带。

    :param 宽带名称: 要连接的宽带的名称。
    :param 用户名: 宽带账户的用户名。
    :param 密码: 宽带账户的密码。
    :return: 一个元组，第一个元素是一个布尔值，表示连接是否成功，第二个元素是连接结果的描述。
    """
    result = subprocess.run(["rasdial", 宽带名称, 用户名, 密码], capture_output=True, text=True, check=True)
    return True


def 系统_断开宽带(宽带名称: str) -> bool:
    """
    尝试断开指定宽带的连接。

    :param 宽带名称: 要断开的宽带的名称。
    :return: 一个元组，第一个元素是一个布尔值，表示断开是否成功，第二个元素是断开结果的描述。
    """
    result = subprocess.run(["rasdial", 宽带名称, "/DISCONNECT"], capture_output=True, text=True, check=True)
    return True


def 系统_设置系统代理(代理状态: bool, 代理地址: str = '') -> bool:
    """
    设置或取消Windows系统代理。

    :param 代理状态: 一个布尔值，指示是否启用代理。
    :param 代理地址: 代理服务器的地址和端口，格式如 '127.0.0.1:8080'。
    :return: 成功返回True,失败返回False
    """
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
                         0, winreg.KEY_ALL_ACCESS)

    def 设置键值(名称, 值):
        _, reg_type = winreg.QueryValueEx(key, 名称)
        winreg.SetValueEx(key, 名称, 0, reg_type, 值)

    设置键值('ProxyEnable', int(代理状态))
    if 代理状态 and 代理地址:
        设置键值('ProxyServer', 代理地址)

    winreg.CloseKey(key)
    return True


def 系统_获取代理状态() -> bool:
    """
    获取Windows系统代理是否启用的状态。

    :return: 如果代理启用，返回True；否则返回False。
    """
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                         0, winreg.KEY_READ)
    try:
        代理状态, _ = winreg.QueryValueEx(key, "ProxyEnable")
        return bool(代理状态)
    finally:
        winreg.CloseKey(key)


def 系统_获取代理地址() -> str:
    """
    获取Windows系统代理服务器的地址。

    :return: 返回代理服务器的地址字符串。如果代理未启用，返回空字符串。
    """
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                         0, winreg.KEY_READ)
    try:
        代理状态, _ = winreg.QueryValueEx(key, "ProxyEnable")
        if bool(代理状态):
            代理服务器, _ = winreg.QueryValueEx(key, "ProxyServer")
            return 代理服务器
        else:
            return ""
    finally:
        winreg.CloseKey(key)


def 系统_是否管理员运行() -> bool:
    """
    检查当前程序是否以管理员权限运行。

    :return: 如果是管理员权限则返回True，否则返回False。
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def 系统_请求管理员权限() -> bool:
    """
    如果当前程序不是以管理员权限运行，则请求提升权限。
    """
    if not 系统_是否管理员运行():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    return True

def 系统_取Python安装目录() -> str:
    """
    获取当前运行的Python解释器的安装目录。

    :return: Python解释器的完整路径。
    """
    return sys.executable

def 系统_取网络接口名() -> list:
    """
    获取当前活动的网络接口名称。

    :return: 包含活动网络接口名称的列表。
    """
    try:
        # 执行ipconfig命令并获取输出
        结果 = subprocess.run(["ipconfig"], capture_output=True, text=True)
        输出 = 结果.stdout

        # 使用正则表达式查找接口名称
        接口名列表 = re.findall(r"适配器 (.+?):", 输出)
        return 接口名列表
    except Exception as e:
        print(f"获取活动网络接口名时出错: {e}")
        return []

def 系统_修改DNS(接口名: str, 主DNS: str, 备用DNS: str = '') -> bool:
    """
    修改指定网络接口的主DNS和备用DNS地址。

    :param 接口名: 要修改的网络接口名称,可通过系统_取网络接口名()获取。
    :param 主DNS: 新的主DNS地址。
    :param 备用DNS: 新的备用DNS地址（可选）。
    :return: 操作成功返回True，否则返回False。

    示例调用：
    - 系统_修改DNS("以太网", "8.8.8.8", "8.8.4.4")
    """
    try:
        网络接口键路径 = f"SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces\\{接口名}"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 网络接口键路径, 0, winreg.KEY_WRITE) as 键:
            DNS设置 = 主DNS
            if 备用DNS:
                DNS设置 += " " + 备用DNS
            winreg.SetValueEx(键, "NameServer", 0, winreg.REG_SZ, DNS设置)

        # 重新应用网络设置
        subprocess.run(["ipconfig", "/flushdns"], check=True)
        subprocess.run(["ipconfig", "/registerdns"], check=True)
        subprocess.run(["ipconfig", "/release"], check=True)
        subprocess.run(["ipconfig", "/renew"], check=True)
        return True
    except Exception as e:
        print(f"修改DNS时出错: {e}")
        return False

def 系统_修改MAC地址(接口名: str, 新MAC地址: str) -> bool:
    """
    修改指定网络接口的MAC地址。

    :param 接口名: 网络接口的名称，例如 "以太网,可通过系统_取网络接口名()获取"。
    :param 新MAC地址: 要设置的新MAC地址。
    :return: 操作成功返回True，否则返回False。

    示例调用：
    - 系统_修改MAC地址("以太网", "00-11-22-33-44-55")
    """
    try:
        网络接口键路径 = f"SYSTEM\\CurrentControlSet\\Control\\Class\\{{4d36e972-e325-11ce-bfc1-08002be10318}}"
        接口键 = None

        # 打开网络适配器注册表
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 网络接口键路径) as 键:
            for i in range(1000):
                try:
                    接口键名 = winreg.EnumKey(键, i)
                    接口键路径 = f"{网络接口键路径}\\{接口键名}"
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 接口键路径) as 接口键:
                        接口值, _ = winreg.QueryValueEx(接口键, "NetCfgInstanceId")
                        if 接口值 == 接口名:
                            break
                except WindowsError:
                    break

        if 接口键 is None:
            raise ValueError("未找到指定的网络接口")

        # 设置新的MAC地址
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 接口键路径, 0, winreg.KEY_WRITE) as 接口键:
            winreg.SetValueEx(接口键, "NetworkAddress", 0, winreg.REG_SZ, 新MAC地址)

        # 重启网络接口以应用更改
        subprocess.run(["netsh", "interface", "set", "interface", 接口名, "disable"], check=True)
        subprocess.run(["netsh", "interface", "set", "interface", 接口名, "enable"], check=True)
        return True
    except Exception as e:
        print(f"修改MAC地址时出错: {e}")
        return False

def 系统_修改主页(新主页: str) -> bool:
    """
    修改Internet Explorer的主页。

    :param 新主页: 要设置的新主页URL。
    :return: 操作成功返回True，否则返回False。

    示例调用：
    - 系统_修改主页("https://www.example.com")
    """
    try:
        键路径 = r"Software\Microsoft\Internet Explorer\Main"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 键路径, 0, winreg.KEY_WRITE) as 键:
            winreg.SetValueEx(键, "Start Page", 0, winreg.REG_SZ, 新主页)
        return True
    except Exception as e:
        print(f"修改主页时出错: {e}")
        return False

def 系统_关机():
    """
    立即关机计算机。
    """
    subprocess.run(["shutdown", "/s", "/f", "/t", "0"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def 系统_注销():
    """
    注销当前用户。
    """
    subprocess.run(["shutdown", "/l"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def 系统_重启():
    """
    重启计算机。
    """
    subprocess.run(["shutdown", "/r", "/f", "/t", "0"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def 系统_重启资源管理器():
    """
    重启Windows资源管理器。
    """
    # 结束资源管理器进程
    subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # 重新启动资源管理器
    subprocess.Popen("explorer.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def 系统_切换用户():
    """
    锁定当前会话，以便用户可以切换到其他账户。
    """
    ctypes.windll.user32.LockWorkStation()

def 系统_取数值注册项(路径: str, 名称: str) -> int:
    """
    从注册表中读取数值型注册项。

    :param 路径: 注册表项的路径。
    :param 名称: 注册表项的名称。
    :return: 注册表项的数值。

    示例调用：
    - print(系统_取数值注册项("HKEY_CURRENT_USER\\Software\\MyApp", "Setting"))
    """
    try:
        根键名, 子键路径 = 路径.split("\\", 1)
        根键 = getattr(winreg, 根键名)
        with winreg.OpenKey(根键, 子键路径) as 键:
            值, 类型 = winreg.QueryValueEx(键, 名称)
            return 值
    except Exception as e:
        print(f"读取数值注册项时出错: {e}")
        return 0

def 系统_取文本注册项(路径: str, 名称: str) -> str:
    """
    从注册表中读取文本型注册项。

    :param 路径: 注册表项的路径。
    :param 名称: 注册表项的名称。
    :return: 注册表项的文本值。

    示例调用：
    - print(系统_取文本注册项("HKEY_CURRENT_USER\\Software\\MyApp", "Setting"))
    """
    try:
        根键名, 子键路径 = 路径.split("\\", 1)
        根键 = getattr(winreg, 根键名)
        with winreg.OpenKey(根键, 子键路径) as 键:
            值, 类型 = winreg.QueryValueEx(键, 名称)
            return 值
    except Exception as e:
        print(f"读取文本注册项时出错: {e}")
        return ""

def 系统_写数值注册项(路径: str, 名称: str, 值: int, 类型: str = "DWORD"):
    """
    写入数值型的注册表项。

    :param 路径: 注册表项的路径。
    :param 名称: 注册表项的名称。
    :param 值: 要写入的数值。
    :param 类型: 注册表项的类型（"DWORD" 或 "QWORD"）。
    :return: 操作成功返回True，否则返回False。

    示例调用：
    - 系统_写数值注册项("HKEY_CURRENT_USER\\Software\\MyApp", "Setting", 1)
    """
    try:
        # 确定根键和子键
        根键名, 子键路径 = 路径.split("\\", 1)
        根键 = getattr(winreg, 根键名)

        # 打开或创建键
        with winreg.CreateKey(根键, 子键路径) as 键:
            if 类型 == "DWORD":
                winreg.SetValueEx(键, 名称, 0, winreg.REG_DWORD, 值)
            elif 类型 == "QWORD":
                winreg.SetValueEx(键, 名称, 0, winreg.REG_QWORD, 值)
        return True
    except Exception as e:
        print(f"写入注册表时出错: {e}")
        return False

def 系统_写文本注册项(路径: str, 名称: str, 值: str):
    """
    写入文本型的注册表项。

    :param 路径: 注册表项的路径。
    :param 名称: 注册表项的名称。
    :param 值: 要写入的文本值。
    :return: 操作成功返回True，否则返回False。

    示例调用：
    - 系统_写文本注册项("HKEY_CURRENT_USER\\Software\\MyApp", "Setting", "value")
    """
    try:
        # 确定根键和子键
        根键名, 子键路径 = 路径.split("\\", 1)
        根键 = getattr(winreg, 根键名)

        # 打开或创建键
        with winreg.CreateKey(根键, 子键路径) as 键:
            winreg.SetValueEx(键, 名称, 0, winreg.REG_SZ, 值)
        return True
    except Exception as e:
        print(f"写入注册表时出错: {e}")
        return False

def 系统_删除注册项(路径: str, 名称: str) -> bool:
    """
    删除指定的注册表项。

    :param 路径: 注册表项的路径。
    :param 名称: 注册表项的名称。
    :return: 操作成功返回True，否则返回False。

    示例调用：
    - 系统_删除注册项("HKEY_CURRENT_USER\\Software\\MyApp", "Setting")
    """
    try:
        根键名, 子键路径 = 路径.split("\\", 1)
        根键 = getattr(winreg, 根键名)
        with winreg.OpenKey(根键, 子键路径, 0, winreg.KEY_WRITE) as 键:
            winreg.DeleteValue(键, 名称)
        return True
    except Exception as e:
        print(f"删除注册表项时出错: {e}")
        return False

def 系统_注册项是否存在(路径: str, 名称: str) -> bool:
    """
    检查指定的注册表项是否存在。

    :param 路径: 注册表项的路径。
    :param 名称: 注册表项的名称。
    :return: 存在返回True，否则返回False。

    示例调用：
    - print(系统_注册项是否存在("HKEY_CURRENT_USER\\Software\\MyApp", "Setting"))
    """
    try:
        根键名, 子键路径 = 路径.split("\\", 1)
        根键 = getattr(winreg, 根键名)
        with winreg.OpenKey(根键, 子键路径) as 键:
            winreg.QueryValueEx(键, 名称)
        return True
    except FileNotFoundError:
        return False

def 系统_是否有摄像头() -> bool:
    """
    检查系统是否有摄像头。

    :return: 如果有摄像头返回True，否则返回False。
    """
    结果 = subprocess.run(["wmic", "path", "Win32_PnPEntity", "where", "DeviceID like 'USB%'", "get", "Name"], capture_output=True, text=True)
    return "摄像头" in 结果.stdout

def 系统_打开任务管理器() -> bool:
    """
    打开Windows任务管理器,需要权限。
    """
    try:
        subprocess.Popen("taskmgr.exe")
        return True
    except Exception as e:
        print(f"打开任务管理器时出错: {e}")
        return False

def 系统_打开控制面板() -> bool:
    """
    打开Windows控制面板。
    """
    try:
        subprocess.Popen(["control"])
        return True
    except Exception as e:
        print(f"打开控制面板时出错: {e}")
        return False

def 系统_打开网络连接属性():
    """
    打开网络连接属性窗口。
    """
    try:
        subprocess.Popen(["control", "ncpa.cpl"])
        return True
    except Exception as e:
        print(f"打开网络连接属性时出错: {e}")
        return False

def 系统_恢复屏保() -> bool:
    """
    恢复屏幕保护程序的默认设置。

    :return: 操作结果字符串。
    """
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_WRITE) as 键:
            屏保激活, _ = winreg.QueryValueEx(键, "ScreenSaveActive")
            if 屏保激活 != "1":
                winreg.SetValueEx(键, "ScreenSaveActive", 0, winreg.REG_SZ, "1")
            return True
    except Exception as e:
        return False

def 系统_去掉屏保():
    """
    禁用Windows的屏幕保护程序。

    示例调用：
    - 系统_去掉屏保()
    """
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_WRITE) as 键:
            winreg.SetValueEx(键, "ScreenSaveActive", 0, winreg.REG_SZ, "0")
        return True
    except Exception as e:
        print(f"去掉屏保时出错: {e}")
        return False


def 系统_取MAC地址() -> str:
    """
    获取计算机的MAC地址。

    :return: MAC地址字符串。
    """
    mac = uuid.getnode()
    mac_str = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
    return mac_str


def 系统_取主页地址() -> str:
    """
    获取Internet Explorer的主页地址。

    :return: 主页地址字符串。
    """
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Internet Explorer\Main") as 键:
            主页地址, _ = winreg.QueryValueEx(键, "Start Page")
            return 主页地址
    except Exception as e:
        return ""

def 系统_取屏幕分辨率() -> tuple:
    """
    获取当前屏幕的分辨率。

    :return: 屏幕分辨率，格式为 (宽度, 高度)。
    """
    user32 = ctypes.windll.user32
    屏幕宽度 = user32.GetSystemMetrics(0)
    屏幕高度 = user32.GetSystemMetrics(1)
    return (屏幕宽度, 屏幕高度)

def 系统_取屏幕数量() -> int:
    """
    获取系统连接的显示器数量。

    :return: 连接的显示器数量。
    """
    user32 = ctypes.windll.user32
    屏幕数量 = user32.GetSystemMetrics(80)  # SM_CMONITORS
    return 屏幕数量

def 系统_取内网IP列表() -> list:
    """
    获取当前设备的内网IP地址。

    :return: 内网IP地址字符串的列表。
    """
    try:
        # 执行ipconfig命令并获取输出
        结果 = subprocess.run(["ipconfig"], capture_output=True, text=True)
        输出 = 结果.stdout
        # 使用正则表达式查找IPv4地址
        匹配 = re.findall(r'IPv4 地址[ .:]*([0-9]+(?:\.[0-9]+){3})', 输出)
        if 匹配:
            return 匹配
    except Exception as e:
        pass
    return []

def 系统_取系统DPI() -> int:
    """
    获取当前系统的DPI设置。

    :return: 系统DPI值。
    """
    # 创建一个设备上下文（DC）对象用于屏幕
    user32 = ctypes.windll.user32
    hdc = user32.GetDC(0)
    # 获取水平DPI值
    DPI = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # 88是水平DPI的索引
    user32.ReleaseDC(0, hdc)
    return DPI

def 系统_取系统信息() -> str:
    """
    获取并返回系统的详细信息。

    :return: 系统信息的字符串。
    """
    try:
        系统信息 = subprocess.check_output("systeminfo", encoding="gbk")
        return 系统信息
    except Exception as e:
        return ""

def 系统_桌面图标显示() -> bool:
    """
    显示桌面图标。
    """
    try:
        SPI_SETICONS = 0x0059
        SPIF_UPDATEINIFILE = 0x01
        SPIF_SENDCHANGE = 0x02
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETICONS, 1, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
        return True
    except Exception as e:
        print(f"显示桌面图标时出错: {e}")
        return False

def 系统_桌面图标隐藏() -> bool:
    """
    隐藏桌面图标。
    """
    try:
        SPI_SETICONS = 0x0059
        SPIF_UPDATEINIFILE = 0x01
        SPIF_SENDCHANGE = 0x02
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETICONS, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
        return True
    except Exception as e:
        print(f"隐藏桌面图标时出错: {e}")
        return False

def 系统_清空回收站() -> bool:
    """
    清空Windows回收站。
    """
    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0)
        return True
    except Exception as e:
        print(f"清空回收站时出错: {e}")
        return False

def 系统_显示我的电脑() -> bool:
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\NewStartPanel', 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, '{20D04FE0-3AEA-1069-A2D8-08002B30309D}', 0, winreg.REG_DWORD, 0)
    winreg.CloseKey(key)
    return True

def 系统_隐藏我的电脑() -> bool:
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\NewStartPanel', 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, '{20D04FE0-3AEA-1069-A2D8-08002B30309D}', 0, winreg.REG_DWORD, 1)
    winreg.CloseKey(key)
    return True

def 系统_隐藏已知文件扩展名() -> bool:
    key_path = r'Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, 'HideFileExt', 0, winreg.REG_DWORD, 1)
    winreg.CloseKey(key)
    return True

def 系统_显示已知文件扩展名() -> bool:
    key_path = r'Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, 'HideFileExt', 0, winreg.REG_DWORD, 0)
    winreg.CloseKey(key)
    return True

def 系统_关闭系统更新() -> bool:
    key_path = r'SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU'
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
    winreg.SetValueEx(key, 'NoAutoUpdate', 0, winreg.REG_DWORD, 1)
    winreg.CloseKey(key)
    return True

def 程序_立即结束():
    """
    立即结束当前运行的Python程序。
    """
    sys.exit()


def 进程_强制结束():
    '使用kill结束当前进程'
    try:
        os.kill(os.getpid(), signal.SIGTERM)  # 发送SIGTERM信号尝试正常结束进程
    except OSError as e:
        print(f"结束进程失败: {e}")


def 进程_结束(进程ID: int):
    """
    结束指定ID的进程。

    :param 进程ID: 要结束的进程的ID。
    """
    try:
        os.kill(进程ID, signal.SIGTERM)  # 发送SIGTERM信号尝试正常结束进程
    except OSError as e:
        print(f"结束进程失败: {e}")


def 进程_取当前进程ID() -> int:
    """
    获取当前运行程序的进程ID。

    :return: 返回当前进程的ID。
    """
    return os.getpid()