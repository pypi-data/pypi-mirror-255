# -*- coding: utf-8 -*-
import win32gui,win32con,win32api,os,ctypes,winreg,win32com.client,win32process
import win32clipboard as w

#字母键
_按键_A,_按键_B,_按键_C,_按键_D,_按键_E,_按键_F,_按键_G,_按键_H,_按键_I,_按键_J,_按键_K,_按键_L,_按键_M,_按键_N,_按键_O,_按键_P,_按键_Q,_按键_R,_按键_S,_按键_T,_按键_U,_按键_V,_按键_W,_按键_X,_按键_Y,_按键_Z = 65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90
#字母上的数字键(左边)
_按键_0_,_按键_1_,_按键_2_,_按键_3_,_按键_4_,_按键_5_,_按键_6_,_按键_7_,_按键_8_,_按键_9_ = 48,49,50,51,52,53,54,55,56,57
#数字键(右边)
_按键_0,_按键_1,_按键_2,_按键_3,_按键_4,_按键_5,_按键_6,_按键_7,_按键_8,_按键_9 = 96,97,98,99,100,101,102,103,104,105
#功能键
_按键_F1,_按键_F2,_按键_F3,_按键_F4,_按键_F5,_按键_F6,_按键_F7,_按键_F8,_按键_F9,_按键_F10,_按键_F11,_按键_F12=112,113,114,115,116,117,118,119,120,121,122,123
#其它键
_按键_乘,_按键_加,_按键_小回车,_按键_减,_按键_点,_按键_除 = 106,107,108,109,110,111
_按键_退格,_按键_TAB,_按键_清除键,_按键_回车,_按键_SHIFT,_按键_CONTROL,_按键_ALT,_按键_大小写键,_按键_ESC,_按键_空格,_按键_PAGE_UP,_按键_PAGE_DOWN,_按键_END,_按键_HOME,_按键_向左,_按键_向右=8,9,12,13,16,17,18,20,27,32,33,34,35,36,37,38
_按键_向右,_按键_向下,_按键_INS,_按键_DEL,_按键_NUM,_按键_冒号键,_按键_等号键,_按键_逗号键,_按键_下划线键,_按键_句号键,_按键_问号键,_按键_波浪键,_按键_左括号,_按键_斜杠键,_按键_右括号,_按键_引号键=39,40,45,46,144,186,187,188,189,190,191,192,219,220,221,222
_按键_音量加,_按键_音量减,_按键_停止,_按键_静音,_按键_浏览器,_按键_邮件,_按键_搜索,_按键_搜餐 = 175,174,179,173,172,180,170,171
_按键_WIN = 91



def 系统_显示任务栏() -> bool:
    """
    显示Windows任务栏。

    :return: 成功显示返回True，失败返回False。
    """
    try:
        # 查找任务栏的窗口句柄
        任务栏句柄 = win32gui.FindWindow("Shell_TrayWnd", None)
        # 显示任务栏
        win32gui.ShowWindow(任务栏句柄, 5)  # 5表示显示窗口
        return True
    except Exception as e:
        print(f"显示任务栏时出错: {e}")
        return False

def 系统_隐藏任务栏() -> bool:
    """
    隐藏Windows任务栏。

    :return: 成功隐藏返回True，失败返回False。
    """
    try:
        # 查找任务栏的窗口句柄
        任务栏句柄 = win32gui.FindWindow("Shell_TrayWnd", None)
        # 隐藏任务栏
        win32gui.ShowWindow(任务栏句柄, 0)  # 0表示隐藏窗口
        return True
    except Exception as e:
        print(f"显示任务栏时出错: {e}")
        return False


def 窗口_句柄取进程ID(窗口句柄: int) -> int:
    """
    根据窗口句柄获取进程ID。

    :param 窗口句柄: 窗口的句柄。
    :return: 进程ID。

    示例调用:
    - 进程ID = 窗口_句柄取进程ID(窗口句柄)
    - print(进程ID)
    """
    _, 进程ID = win32process.GetWindowThreadProcessId(窗口句柄)
    return 进程ID


def 窗口_取窗口句柄(类名: str = None, 标题: str = None) -> int:
    """
    根据类名和标题查找窗口，并返回窗口的句柄。

    :param 类名: 窗口的类名。
    :param 标题: 窗口的标题。
    :return: 找到的窗口句柄，如果未找到则返回0。

    示例调用：
    - print(窗口_取窗口句柄(None, "计算器"))
    预期输出：
    - 返回计算器窗口的句柄（如果计算器窗口打开）
    """
    return win32gui.FindWindow(类名, 标题)

def 窗口_取坐标处窗口句柄(x: int, y: int) -> int:
    """
    返回指定坐标处的窗口句柄。

    :param x: 屏幕上的x坐标。
    :param y: 屏幕上的y坐标。
    :return: 坐标处窗口的句柄。
    """
    return win32gui.WindowFromPoint((x, y))

def 窗口_置父窗口(子窗口句柄: int, 父窗口句柄: int) -> int:
    """
    将子窗口嵌入到指定的父窗口内。

    :param 子窗口句柄: 子窗口的句柄。
    :param 父窗口句柄: 父窗口的句柄。
    :return: 操作成功时返回非零值，失败时返回零。
    """
    return win32gui.SetParent(子窗口句柄, 父窗口句柄)

def 窗口_取窗口类名(窗口句柄: int) -> str:
    """
    返回给定窗口句柄的窗口类名。

    :param 窗口句柄: 窗口的句柄。
    :return: 窗口的类名。

    示例调用：
    - 句柄 = 窗口_取窗口句柄(None, "计算器")
    - print(窗口_取窗口类名(句柄))
    预期输出：
    - 返回计算器窗口的类名
    """
    return win32gui.GetClassName(窗口句柄)

def 窗口_取窗口标题(窗口句柄: int) -> str:
    """
    返回给定窗口句柄的窗口标题。

    :param 窗口句柄: 窗口的句柄。
    :return: 窗口的标题。

    示例调用：
    - 句柄 = 窗口_取窗口句柄(None, "记事本")
    - print(窗口_取窗口标题(句柄))
    预期输出：
    - 返回记事本窗口的标题
    """
    return win32gui.GetWindowText(窗口句柄)

def 窗口_取窗口矩形(窗口句柄: int) -> tuple:
    """
    获取指定窗口的矩形区域。

    :param 窗口句柄: 窗口的句柄。
    :return: 成功返回窗口的矩形区域（左边, 顶边, 右边, 底边），失败返回None。
    """
    try:
        return win32gui.GetWindowRect(窗口句柄)
    except Exception as e:
        print(f"获取窗口矩形时出错: {e}")
        return None

def 窗口_枚举子窗口句柄(窗口句柄: int) -> list:
    """
    枚举指定窗口的所有子窗口句柄。

    :param 窗口句柄: 窗口的句柄。
    :return: 子窗口句柄的列表。
    """
    hwndChildList = []
    win32gui.EnumChildWindows(窗口句柄, lambda hwnd, param: param.append(hwnd), hwndChildList)
    return hwndChildList

def 窗口_取窗口文本(窗口句柄: int) -> str:
    """
    获取指定窗口的文本内容。

    :param 窗口句柄: 窗口的句柄。
    :return: 窗口的文本内容。
    """
    # 获取文本框内容长度
    length = win32gui.SendMessage(窗口句柄, win32con.WM_GETTEXTLENGTH) + 1
    # 创建缓冲区
    buf = ctypes.create_unicode_buffer(length)
    # 发送获取文本消息
    win32gui.SendMessage(窗口句柄, win32con.WM_GETTEXT, length, buf)
    # 返回窗口文本
    return buf.value

def 窗口_发送文本(窗口句柄: int, 内容: str) -> int:
    """
    向指定窗口发送文本。

    :param 窗口句柄: 窗口的句柄。
    :param 内容: 要发送的文本内容。
    :return: 消息处理的结果。
    """
    return win32api.SendMessage(窗口句柄, win32con.WM_SETTEXT, 0, 内容)

def 窗口_取窗口文本长度(窗口句柄: int) -> int:
    """
    获取指定窗口文本的长度。

    :param 窗口句柄: 窗口的句柄。
    :return: 窗口文本的长度（包括终止字符）。
    """
    return win32api.SendMessage(窗口句柄, win32con.WM_GETTEXTLENGTH, 0, 0) + 1

def 窗口_发送信息(窗口句柄: int, 消息类型: int, 参数1: int = 0, 参数2: int = 0) -> bool:
    """
    向指定窗口发送消息（非阻塞方式）。

    :param 窗口句柄: 窗口的句柄。
    :param 消息类型: 要发送的消息类型。
    :param 参数1: 消息的第一个参数。
    :param 参数2: 消息的第二个参数。
    :return: 消息发送成功返回True，否则返回False。
    """
    return win32gui.PostMessage(窗口句柄, 消息类型, 参数1, 参数2)

def 窗口_发送信息2(窗口句柄: int, 消息类型: int, 参数1: int = 0, 参数2: int = 0) -> int:
    """
    向指定窗口发送消息（阻塞方式）。

    :param 窗口句柄: 窗口的句柄。
    :param 消息类型: 要发送的消息类型。
    :param 参数1: 消息的第一个参数。
    :param 参数2: 消息的第二个参数。
    :return: 消息处理的结果。
    """
    return win32gui.SendMessage(窗口句柄, 消息类型, 参数1, 参数2)

def 窗口_关闭窗口(窗口句柄: int) -> bool:
    """
    发送消息以关闭指定窗口。

    :param 窗口句柄: 窗口的句柄。
    :return: 发送消息成功返回True，否则返回False。
    """
    return win32gui.PostMessage(窗口句柄, win32con.WM_CLOSE, 0, 0)

def 窗口_是否最小化(窗口句柄: int) -> bool:
    """
    检查指定窗口是否已最小化。

    :param 窗口句柄: 窗口的句柄。
    :return: 如果窗口已最小化则返回True，否则返回False。
    """
    return bool(win32gui.IsIconic(窗口句柄))

def 窗口_最大化(窗口句柄: int) -> bool:
    """
    最大化指定的窗口。

    :param 窗口句柄: 窗口的句柄。
    :return: 操作成功返回True，否则返回False。
    """
    return bool(win32gui.ShowWindow(窗口句柄, win32con.SW_MAXIMIZE))

def 窗口_最大化并激活(窗口句柄: int) -> bool:
    """
    激活窗口并将其最大化。

    :param 窗口句柄: 窗口的句柄。
    :return: 操作成功返回True，否则返回False。
    """
    return bool(win32gui.ShowWindow(窗口句柄, win32con.SW_SHOWMAXIMIZED))

def 窗口_最小化(窗口句柄: int) -> bool:
    """
    最小化指定的窗口。

    :param 窗口句柄: 窗口的句柄。
    :return: 操作成功返回True，否则返回False。
    """
    return bool(win32gui.ShowWindow(窗口句柄, win32con.SW_MINIMIZE))

def 窗口_最小化并激活(窗口句柄: int) -> bool:
    """
    激活窗口并将其最小化。

    :param 窗口句柄: 窗口的句柄。
    :return: 操作成功返回True，否则返回False。
    """
    return bool(win32gui.ShowWindow(窗口句柄, win32con.SW_SHOWMINIMIZED))

def 窗口_最小化并保持激活(窗口句柄: int) -> bool:
    """
    将指定窗口最小化，同时保持当前激活的窗口不变。

    :param 窗口句柄: 窗口的句柄。
    :return: 操作成功返回True，否则返回False。
    """
    return bool(win32gui.ShowWindow(窗口句柄, win32con.SW_SHOWMINNOACTIVE))

def 窗口_隐藏窗口(窗口句柄: int) -> bool:
    """
    隐藏指定的窗口。

    :param 窗口句柄: 窗口的句柄。
    :return: 操作成功返回True，否则返回False。
    """
    return bool(win32gui.ShowWindow(窗口句柄, win32con.SW_HIDE))

def 窗口_显示窗口(窗口句柄: int) -> bool:
    """
    显示窗口。

    :param 窗口句柄: 窗口的句柄。
    :return: 操作成功返回True，否则返回False。
    """
    return bool(win32gui.ShowWindow(窗口句柄, win32con.SW_SHOW))



def 窗口_原尺寸显示窗口(窗口句柄: int) -> bool:
    """
    以原尺寸恢复显示窗口。

    :param 窗口句柄: 窗口的句柄。
    :return: 操作成功返回True，否则返回False。
    """
    return bool(win32gui.ShowWindow(窗口句柄, win32con.SW_RESTORE))

def 窗口_原状态显示窗口(窗口句柄: int) -> bool:
    """
    以窗口原来的状态显示窗口。激活窗口仍然维持激活状态。

    :param 窗口句柄: 窗口的句柄。
    :return: 操作成功返回True，否则返回False。
    """
    return bool(win32gui.ShowWindow(窗口句柄, win32con.SW_SHOWNA))

def 窗口_最近状态显示窗口(窗口句柄: int) -> bool:
    """
    以窗口最近一次的大小和状态显示窗口。激活窗口仍然维持激活状态。

    :param 窗口句柄: 窗口的句柄。
    :return: 操作成功返回True，否则返回False。
    """
    return bool(win32gui.ShowWindow(窗口句柄, win32con.SW_SHOWNOACTIVATE))

def 窗口_激活并显示窗口(窗口句柄: int) -> bool:
    """
    激活并显示一个窗口。如果窗口被最小化或最大化，系统将其恢复到原来的尺寸和大小。

    :param 窗口句柄: 窗口的句柄。
    :return: 操作成功返回True，否则返回False。
    """
    return bool(win32gui.ShowWindow(窗口句柄, win32con.SW_SHOWNORMAL))

def 窗口_调整(窗口句柄: int, 左边: int, 顶边: int, 宽度: int, 高度: int) -> bool:
    """
    移动窗口并调整其宽度和高度。

    :param 窗口句柄: 窗口的句柄。
    :param 左边: 窗口新位置的左边界。
    :param 顶边: 窗口新位置的上边界。
    :param 宽度: 窗口的新宽度。
    :param 高度: 窗口的新高度。
    :return: 操作成功返回True，否则返回False。
    """
    return win32gui.MoveWindow(窗口句柄, 左边, 顶边, 宽度, 高度, True)

def 窗口_调整并置顶(窗口句柄: int, 左边: int, 顶边: int, 宽度: int, 高度: int) -> bool:
    """
    移动窗口并调整其宽度和高度，将窗口置于最上层。

    :param 窗口句柄: 窗口的句柄。
    :param 左边: 窗口新位置的左边界。
    :param 顶边: 窗口新位置的上边界。
    :param 宽度: 窗口的新宽度。
    :param 高度: 窗口的新高度。
    :return: 操作成功返回True，否则返回False。
    """
    return win32gui.SetWindowPos(窗口句柄, win32con.HWND_TOPMOST, 左边, 顶边, 宽度, 高度, win32con.SWP_SHOWWINDOW)

def 窗口_总在最前(窗口句柄: int):
    """
    将指定窗口设置为总在最前。

    :param 窗口句柄: 目标窗口的句柄。
    :return: 无返回值。

    示例调用：
    - 窗口_总在最前(窗口句柄)
    """
    win32gui.SetWindowPos(窗口句柄, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

def 窗口_置前台(窗口句柄: int) -> bool:
    """
    将指定窗口设置为前台窗口。

    :param 窗口句柄: 窗口的句柄。
    :return: 操作成功返回True，否则返回False。
    """
    return win32gui.SetForegroundWindow(窗口句柄)

def 窗口_置后台(窗口句柄: int) -> bool:
    """
    将指定窗口设置为后台窗口。

    :param 窗口句柄: 窗口的句柄。
    :return: 操作成功返回True，否则返回False。
    """
    return win32gui.SetBkMode(窗口句柄, win32con.TRANSPARENT)

def _MyCallback(hwnd, extra):
    """
    回调函数，用于 `EnumWindows` 枚举窗口时收集窗口信息。

    :param hwnd: 窗口句柄。
    :param extra: 传递的额外参数，这里是存储窗口信息的字典。
    """
    windows = extra
    temp = [hex(hwnd), win32gui.GetClassName(hwnd), win32gui.GetWindowText(hwnd)]
    windows[hwnd] = temp

def 窗口_枚举子窗口(窗口句柄: int) -> list:
    """
    枚举指定窗口的直接子窗口句柄。

    :param 窗口句柄: 目标窗口的句柄。
    :return: 子窗口句柄的列表。
    """
    子句柄列表 = []

    def 枚举回调(句柄, lParam):
        子句柄列表.append(句柄)
        return True

    win32gui.EnumChildWindows(窗口句柄, 枚举回调, None)
    return 子句柄列表

def 窗口_枚举所有子窗口(窗口句柄: int) -> list:
    """
    递归枚举指定窗口的所有子窗口句柄。

    :param 窗口句柄: 目标窗口的句柄。
    :return: 所有子窗口句柄的列表。
    """
    所有子句柄列表 = []

    def 枚举回调(句柄, lParam):
        所有子句柄列表.append(句柄)
        窗口_枚举所有子窗口(句柄)  # 递归调用以获取更深层次的子窗口
        return True

    win32gui.EnumChildWindows(窗口句柄, 枚举回调, None)
    return 所有子句柄列表

def 窗口_取所有顶级窗口句柄() -> dict:
    """
    返回所有顶级窗口的句柄及其相关信息。

    :return: 字典，键为窗口句柄，值为列表（[句柄的十六进制表示, 窗口类名, 窗口标题]）。
    """
    windows = {}
    win32gui.EnumWindows(_MyCallback, windows)
    return windows

def 窗口_发送拖放消息(窗口句柄, 文件路径列表) -> bool:
    """
    向指定窗口发送模拟拖放文件的消息。

    :param 窗口句柄: 目标窗口的句柄。
    :param 文件路径列表: 要拖放的文件路径列表。
    :return: 成功返回True,失败返回False。
    示例调用：
    - 窗口_发送拖放消息(窗口句柄, ['C:\\path\\to\\file1.txt', 'C:\\path\\to\\file2.txt'])
    """
    # 示例：发送简化的拖放消息
    # 注意：这是一个非常简化的示例，实际情况可能需要更复杂的消息序列和处理
    for 文件路径 in 文件路径列表:
        # 发送文件路径
        win32api.SendMessage(窗口句柄, win32con.WM_DROPFILES, 文件路径, 0)
    return True

def 窗口_取句柄_模糊(部分标题: str) -> list:
    """
    通过部分窗口标题模糊搜索窗口句柄。

    :param 部分标题: 需要匹配的窗口标题的一部分。
    :return: 返回包含匹配的窗口句柄的列表。
    """
    句柄列表 = []

    def 枚举窗口(句柄, lParam):
        if 部分标题 in win32gui.GetWindowText(句柄):
            句柄列表.append(句柄)
        return True

    win32gui.EnumWindows(枚举窗口, None)
    return 句柄列表

def 窗口_取屏幕句柄() -> int:
    """
    获取代表整个屏幕的窗口句柄。

    :return: 屏幕的窗口句柄。
    """
    return win32gui.GetDesktopWindow()

def 窗口_取桌面句柄() -> int:
    """
    获取代表桌面的窗口句柄。

    :return: 桌面的窗口句柄。
    """
    return win32gui.GetShellWindow()

def 窗口_句柄取类名(窗口句柄: int) -> str:
    """
    获取指定窗口的类名。

    :param 窗口句柄: 目标窗口的句柄。
    :return: 窗口的类名。
    """
    return win32gui.GetClassName(窗口句柄)

def 窗口_取父句柄(窗口句柄: int) -> int:
    """
    获取指定窗口的父窗口句柄。

    :param 窗口句柄: 目标窗口的句柄。
    :return: 父窗口的句柄。
    """
    return win32gui.GetParent(窗口句柄)

def 窗口_取祖句柄(窗口句柄: int) -> int:
    """
    获取指定窗口的祖窗口句柄。

    :param 窗口句柄: 目标窗口的句柄。
    :return: 祖窗口的句柄。
    """
    return win32gui.GetAncestor(窗口句柄, win32con.GA_ROOT)

def 窗口_取消尺寸限制(窗口句柄: int):
    """
    取消对指定窗口尺寸的限制。

    :param 窗口句柄: 目标窗口的句柄。
    :return: 无返回值。
    """
    win32gui.SetWindowLong(窗口句柄, win32con.GWL_WNDPROC, win32gui.DefWindowProc)




def 鼠标_移动(x: int, y: int):
    """
    在桌面上移动鼠标到指定的坐标位置。

    :param x: 目标位置的X坐标。
    :param y: 目标位置的Y坐标。
    """
    win32api.SetCursorPos((x, y))

def 鼠标_点击(按键: int = 0, 类型: int = 0, x: int = 0, y: int = 0):
    """
    模拟鼠标点击。

    :param 按键: 模拟的鼠标按键，0-左键，1-中键，2-右键。
    :param 类型: 点击的类型，0-单击，1-按下，2-弹起。
    :param x: 鼠标位置的X坐标。
    :param y: 鼠标位置的Y坐标。
    """
    代码映射 = {(0, 1): win32con.MOUSEEVENTF_LEFTDOWN,
               (0, 2): win32con.MOUSEEVENTF_LEFTUP,
               (1, 1): win32con.MOUSEEVENTF_MIDDLEDOWN,
               (1, 2): win32con.MOUSEEVENTF_MIDDLEUP,
               (2, 1): win32con.MOUSEEVENTF_RIGHTDOWN,
               (2, 2): win32con.MOUSEEVENTF_RIGHTUP}

    if (按键, 类型) in 代码映射:
        win32api.mouse_event(代码映射[(按键, 类型)], x, y, 0, 0)
    else:
        # 默认为左键单击
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

def 键盘_点击(键码: int, 类型: int = 0) -> None:
    """
    模拟键盘按键点击。

    :param 键码: 要模拟的按键的键码,可使用 _按键_**。
    :param 类型: 按键操作的类型，0-单击，1-按下，2-弹起。
    :return: 无。
    """
    if 类型 == 1:
        win32api.keybd_event(键码, 0, 0, 0)
    elif 类型 == 2:
        win32api.keybd_event(键码, 0, win32con.KEYEVENTF_KEYUP, 0)
    else:
        win32api.keybd_event(键码, 0, 0, 0)
        win32api.keybd_event(键码, 0, win32con.KEYEVENTF_KEYUP, 0)


def 取剪辑版文本(编码:str='gbk') -> str:
    """
    获取剪贴板上的文本内容。
    :param 编码: 常规用utf8带汉字的用gbk等,默认gbk。
    :return: 剪贴板上的文本内容。
    """
    w.OpenClipboard()
    d = w.GetClipboardData(win32con.CF_TEXT)
    w.CloseClipboard()
    return d.decode(编码) # 或根据需要使用不同的编码方式


def 置剪辑版文本(内容: str) -> bool:
    """
    设置剪贴板上的文本内容。

    :param 内容: 要设置到剪贴板的文本。
    :return: 操作成功返回True。
    """
    w.OpenClipboard()
    w.EmptyClipboard()
    w.SetClipboardText(内容)
    w.CloseClipboard()
    return True

def 运行(文件路径: str, 参数: str = '', 初始目录: str = '', 显示窗口: bool = True) -> int:
    """
    启动或运行一个指定的程序或文件。

    :param 文件路径: 要运行的程序或文件的路径。
    :param 参数: 传递给程序的参数。
    :param 初始目录: 程序的初始目录。
    :param 显示窗口: 是否显示程序窗口。
    :return: 操作的返回值。
    """
    显示命令 = win32con.SW_SHOW if 显示窗口 else win32con.SW_HIDE
    return win32api.ShellExecute(0, 'open', 文件路径, 参数, 初始目录, 显示命令)

def 信息框(内容: str, 标题: str = '提示', 类型: int = 0, 图标: int = 0) -> int:
    """
    使用Windows API创建一个信息框。

    :param 内容: 消息框显示的内容。
    :param 标题: 消息框的标题。
    :param 类型: 消息框的按钮类型。0-通常，1-确定取消，2-是否，3-是否取消，4-终止重试忽略。
    :param 图标: 消息框的图标类型。0-没有，1-蓝色提示，2-黄色感叹，3-红色叉叉。
    :return: 用户响应的结果代码。1-确定，2-取消，3-中止，4-重试，5-忽略，6-是，7-否。
    """
    按钮类型 = {0: win32con.MB_OK, 1: win32con.MB_OKCANCEL, 2: win32con.MB_YESNO,
               3: win32con.MB_YESNOCANCEL, 4: win32con.MB_ABORTRETRYIGNORE}
    图标类型 = {0: 0, 1: win32con.MB_ICONASTERISK, 2: win32con.MB_ICONEXCLAMATION,
               3: win32con.MB_ICONERROR}
    return win32api.MessageBox(0, 内容, 标题, 按钮类型[类型] | 图标类型[图标])

def 系统_关联文件后缀(后缀: str, 程序路径: str, 描述: str = '', 图标路径: str = '') -> bool:
    """
    将指定的文件后缀名与程序关联，并可选地设置图标。

    :param 后缀: 要关联的文件后缀名，例如 '.txt'。
    :param 程序路径: 与该后缀名关联的程序的完整路径。
    :param 描述: 文件类型的描述。
    :param 图标路径: 文件类型的图标路径。
    :return: 操作成功返回True，否则返回False。

    示例调用：
    - 关联文件后缀('.abc', 'C:\\Path\\To\\YourApp.exe', 'ABC文件', 'C:\\Path\\To\\Icon.ico')
    """
    try:
        # 打开或创建后缀名的注册表键
        key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 后缀)
        winreg.SetValue(key, '', winreg.REG_SZ, 描述)
        winreg.CloseKey(key)

        # 设置打开命令
        command = f'"{程序路径}" "%1"'
        key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f'{后缀}\\shell\\open\\command')
        winreg.SetValue(key, '', winreg.REG_SZ, command)
        winreg.CloseKey(key)

        # 可选：设置图标
        if 图标路径:
            key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f'{后缀}\\DefaultIcon')
            winreg.SetValue(key, '', winreg.REG_SZ, 图标路径)
            winreg.CloseKey(key)

        return True
    except Exception as e:
        print(f"关联文件后缀时出错: {e}")
        return False

def 系统_创建桌面快捷方式(目标路径: str, 快捷方式名: str, 快捷方式描述: str = '', 图标路径: str = ''):
    """
    在桌面创建一个快捷方式。

    :param 目标路径: 快捷方式指向的目标文件路径。
    :param 快捷方式名: 快捷方式的名称。
    :param 快捷方式描述: 快捷方式的描述（可选）。
    :param 图标路径: 快捷方式的图标路径（可选）。
    :return: 操作成功返回True，否则返回False。

    示例调用：
    - 系统_创建桌面快捷方式("C:\\Path\\To\\App.exe", "我的应用")
    """
    try:
        桌面路径 = os.path.join(os.path.expanduser("~"), "Desktop")
        快捷方式完整路径 = os.path.join(桌面路径, 快捷方式名 + ".lnk")

        shell = win32com.client.Dispatch("WScript.Shell")
        快捷方式 = shell.CreateShortcut(快捷方式完整路径)
        快捷方式.Targetpath = 目标路径
        快捷方式.Description = 快捷方式描述
        if 图标路径:
            快捷方式.IconLocation = 图标路径
        快捷方式.save()
        return True
    except Exception as e:
        print(f"创建桌面快捷方式时出错: {e}")
        return False


def 文件_置隐藏(路径: str) -> bool:
    """
    设置文件或目录为隐藏。

    :param 路径: 文件或目录的路径。
    :return: 操作成功返回True。
    """
    win32api.SetFileAttributes(路径, win32con.FILE_ATTRIBUTE_HIDDEN)
    return True

def 文件_置只读(路径: str) -> bool:
    """
    设置文件为只读。

    :param 路径: 文件的路径。
    :return: 操作成功返回True。
    """
    win32api.SetFileAttributes(路径, win32con.FILE_ATTRIBUTE_READONLY)
    return True

def 文件_置系统文件(路径: str) -> bool:
    """
    设置文件为系统文件。

    :param 路径: 文件的路径。
    :return: 操作成功返回True。
    """
    win32api.SetFileAttributes(路径, win32con.FILE_ATTRIBUTE_SYSTEM)
    return True

def 文件_恢复常规属性(路径: str) -> bool:
    """
    将文件的属性设置为正常。

    :param 路径: 文件的路径。
    :return: 操作成功返回True。
    """
    win32api.SetFileAttributes(路径, win32con.FILE_ATTRIBUTE_NORMAL)
    return True


def 系统_刷新():
    """
    立即刷新系统，使注册表新的设置立即生效。
    """
    HWND_BROADCAST = 0xFFFF
    WM_SETTINGCHANGE = win32con.WM_SETTINGCHANGE
    SMTO_ABORTIFHUNG = 0x0002

    ctypes.windll.user32.SendMessageTimeoutW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", SMTO_ABORTIFHUNG, 5000, None)

def 系统_刷新屏幕():
    """
    刷新屏幕，强制重绘桌面和所有窗口。
    """
    # 发送刷新消息到所有顶级窗口
    HWND_BROADCAST = 0xFFFF
    WM_PAINT = win32con.WM_PAINT
    ctypes.windll.user32.SendMessageTimeoutW(HWND_BROADCAST, WM_PAINT, 0, 0, 0, 1000, None)




