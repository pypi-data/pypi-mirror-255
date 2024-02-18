# -*- coding:utf-8 -*-
import wx,wx.adv,wx.lib
import wx.lib.agw.floatspin as lib_fs
import wx.lib.agw.hyperlink as lib_hyperlink
import wx.lib.agw.gradientbutton as lib_gb
import wx.lib.buttons as lib_button
import wx.propgrid

def 组件_取窗口句柄(组件):
    """
    取wxPython组件的窗口句柄。

    :param 组件: wxPython中的组件。
    :return: 组件的窗口句柄。
    示例：句柄 = 组件_取窗口句柄(某个wxPython组件)
    """
    return 组件.GetHandle()


def 组件_取组件祖组件(组件):
    """
    取wxPython组件的上上层组件，即组件的祖组件。
    结构通常为[当前组件-父组件-祖组件]。

    :param 组件: wxPython中的组件。
    :return: 组件的祖组件。
    示例：祖组件 = 组件_取组件祖组件(某个wxPython组件)
    """
    return 组件.GetGrandParent()


def 组件_对齐(组件, 方向=12):
    """
    默认居中，使组件在父组件内对齐，主窗口则在屏幕中间。
    方向：1.左上 4/5.顶边 8/9.左边 12/13.居中。

    :param 组件: wxPython中的组件。
    :param 方向: 对齐方向。
    :return: 无。
    示例：组件_对齐(某个wxPython组件, 12) # 居中对齐
    """
    return 组件.Center(方向)


def 组件_取桌面相对坐标(组件, x=0, y=0):
    """
    返回相对于此组件的坐标转换为屏幕坐标，x,y为偏移位置，0为当前。

    :param 组件: wxPython中的组件。
    :param x: x坐标偏移。
    :param y: y坐标偏移。
    :return: 屏幕坐标。
    示例：屏幕坐标 = 组件_取桌面相对坐标(某个wxPython组件, 10, 10)
    """
    return 组件.ClientToScreen(x, y)


def 组件_关闭(窗口):
    """
    用来关闭窗口。

    :param 窗口: wxPython中的窗口。
    :return: 无。
    示例：组件_关闭(某个wxPython窗口)
    """
    return 窗口.Close(True)

def 组件_销毁(窗口):
    """
    销毁窗口。备注：这个方法不会立即销毁窗口，会等事件执行后才安全地销毁。

    :param 窗口: wxPython中的窗口。
    :return: 无。
    示例：组件_销毁(某个wxPython窗口)
    """
    return 窗口.Destroy()

def 组件_销毁所有子窗口(组件):
    """
    销毁窗口下所有的子窗口和组件。

    :param 组件: wxPython中的组件。
    :return: 无。
    示例：组件_销毁所有子窗口(某个wxPython组件)
    """
    return 组件.DestroyChildren()

def 组件_销毁2(窗口):
    """
    官方解释：计划在不久的将来销毁该窗口。应在销毁可能发生得太早时使用此方法（例如，当窗口或其子级仍在事件队列中等待时）。

    :param 窗口: wxPython中的窗口。
    :return: 无。
    示例：组件_销毁2(某个wxPython窗口)
    """
    return 窗口.DestroyLater()

def 组件_禁用(组件):
    """
    禁用组件。禁用后，组件及其所有子级都将无法进行用户交互。

    :param 组件: wxPython中的组件。
    :return: 无。
    示例：组件_禁用(某个wxPython组件)
    """
    return 组件.Disable()

def 组件_禁用2(组件):
    """
    禁用组件用于用户输入。

    :param 组件: wxPython中的组件。
    :return: 无。
    示例：组件_禁用2(某个wxPython组件)
    """
    return 组件.Enable(False)

def 组件_允许拖放文件(组件, 允许=True):
    """
    设置组件是否允许接收拖放文件。

    :param 组件: wxPython中的组件。
    :param 允许: 是否允许拖放文件，默认为True。
    :return: 无。
    示例：组件_允许拖放文件(某个wxPython组件)
    """
    return 组件.DragAcceptFiles(允许)

def 组件_ID匹配组件(父窗口, id):
    """
    在父窗口下查找并返回具有指定ID的组件。

    :param 父窗口: wxPython中的父窗口。
    :param id: 组件的ID。
    :return: 匹配到的组件。
    示例：组件 = 组件_ID匹配组件(某个wxPython父窗口, 某ID)
    """
    return 父窗口.FindWindowById(id)

def 组件_ID匹配组件2(父窗口, id):
    """
    在父窗口下查找并返回匹配到的第一个具有指定ID的组件。

    :param 父窗口: wxPython中的父窗口。
    :param id: 组件的ID。
    :return: 匹配到的组件。
    示例：组件 = 组件_ID匹配组件2(某个wxPython父窗口, 某ID)
    """
    return 父窗口.FindWindow(id)

def 组件_取键盘焦点组件(父窗口):
    """
    在父窗口下查找当前具有键盘焦点的窗口或控件。

    :param 父窗口: wxPython中的父窗口。
    :return: 具有键盘焦点的组件。
    示例：焦点组件 = 组件_取键盘焦点组件(某个wxPython父窗口)
    """
    return 父窗口.FindFocus()

def 组件_标题匹配组件(父窗口, 标题):
    """
    通过组件标题查找并返回匹配到的第一个组件。

    :param 父窗口: wxPython中的父窗口。
    :param 标题: 组件的标题。
    :return: 匹配到的组件。
    示例：组件 = 组件_标题匹配组件(某个wxPython父窗口, '标题')
    """
    return 父窗口.FindWindowByLabel(标题)

def 组件_名称匹配组件(父窗口, 组件名):
    """
    通过组件名查找并返回匹配到的第一个组件。

    :param 父窗口: wxPython中的父窗口。
    :param 组件名: 组件的名称。
    :return: 匹配到的组件。
    示例：组件 = 组件_名称匹配组件(某个wxPython父窗口, '组件名')
    """
    return 父窗口.FindWindowByName(组件名)

def 组件_自动调整尺寸(组件):
    """
    调整窗口大小以适合其最佳大小。

    :param 组件: wxPython中的组件。
    :return: 无。
    示例：组件_自动调整尺寸(某个wxPython组件)
    """
    return 组件.Fit()

def 组件_自动调整内部尺寸(组件):
    """
    调整窗口的内部（虚拟）尺寸。主要用于滚动窗口，以重置滚动条或调整大小而不触发大小事件。
    如果没有子窗口，此方法不会执行任何操作。

    :param 组件: wxPython中的组件。
    :return: 无。
    示例：组件_自动调整内部尺寸(某个wxPython组件)
    """
    return 组件.FitInside()

def 组件_禁止重画(组件):
    """
    冻结窗口，即阻止任何更新在屏幕上发生，窗口不会重绘。

    :param 组件: wxPython中的组件。
    :return: 无。
    示例：组件_禁止重画(某个wxPython组件)
    """
    return 组件.Freeze()

def 组件_允许重画(组件):
    """
    重新启用窗口更新。

    :param 组件: wxPython中的组件。
    :return: 无。
    示例：组件_允许重画(某个wxPython组件)
    """
    return 组件.Thaw()

def 组件_取背景颜色(组件):
    """
    返回窗口的背景色。

    :param 组件: wxPython中的组件。
    :return: 背景色，格式为(240, 240, 240, 255)。
    示例：颜色 = 组件_取背景颜色(某个wxPython组件)
    """
    return 组件.GetBackgroundColour()

def 组件_取样式(组件):
    """
    返回窗口的背景样式。

    :param 组件: wxPython中的组件。
    :return: 背景样式值。
    示例：样式 = 组件_取样式(某个wxPython组件)
    """
    return 组件.GetBackgroundStyle()

def 组件_取最小可接受尺寸(组件):
    """
    获取窗口的最佳可接受最小尺寸。

    :param 组件: wxPython中的组件。
    :return: 最小可接受尺寸，返回格式为(宽度, 高度)。高度不包含标题栏高度。
    示例：尺寸 = 组件_取最小可接受尺寸(某个wxPython组件)
    """
    return 组件.GetBestSize()

def 组件_取最大可接受尺寸(组件):
    """
    获取窗口的最佳可接受最大尺寸。

    :param 组件: wxPython中的组件。
    :return: 最大可接受尺寸，返回格式为(宽度, 高度)。高度不包含标题栏高度。
    示例：尺寸 = 组件_取最大可接受尺寸(某个wxPython组件)
    """
    return 组件.GetBestVirtualSize()

def 组件_取边框样式(组件):
    """
    获取此窗口的边框样式。

    :param 组件: wxPython中的组件。
    :return: 边框样式。
    示例：样式 = 组件_取边框样式(某个wxPython组件)
    """
    return 组件.GetBorder()

def 组件_取额外样式(组件):
    """
    获取窗口的额外样式位。

    :param 组件: wxPython中的组件。
    :return: 额外样式位。
    示例：样式 = 组件_取额外样式(某个wxPython组件)
    """
    return 组件.GetExtraStyle()

def 组件_取字体高度(组件):
    """
    返回此窗口的字符高度。

    :param 组件: wxPython中的组件。
    :return: 字符高度。
    示例：高度 = 组件_取字体高度(某个wxPython组件)
    """
    return 组件.GetCharHeight()

def 组件_取平均字符宽度(组件):
    """
    返回此窗口的平均字符宽度。

    :param 组件: wxPython中的组件。
    :return: 平均字符宽度。
    示例：宽度 = 组件_取平均字符宽度(某个wxPython组件)
    """
    return 组件.GetCharWidth()

def 组件_遍历下级组件(组件):
    """
    遍历组件下的子级组件。

    :param 组件: wxPython中的组件。
    :return: 子级组件列表。
    示例：子级组件列表 = 组件_遍历下级组件(某个wxPython组件)
    """
    return 组件.GetChildren()

def 组件_取字体及颜色(组件):
    """
    返回组件的字体、背景颜色和前景颜色。

    :param 组件: wxPython中的组件。
    :return: 字体，背景颜色，前景颜色。
    示例：字体, 背景颜色, 前景颜色 = 组件_取字体及颜色(某个wxPython组件)
    """
    结果 = 组件.GetClassDefaultAttributes()
    return 结果.font, 结果.colBg, 结果.colFg

def 组件_取矩形(组件):
    """
    返回组件的矩形区域。

    :param 组件: wxPython中的组件。
    :return: 矩形区域，格式为(左边, 顶边, 宽度, 高度)。
    示例：矩形 = 组件_取矩形(某个wxPython组件)
    """
    return 组件.GetRect()

def 组件_取矩形2(组件):
    """
    返回组件的客户区矩形区域。

    :param 组件: wxPython中的组件。
    :return: 矩形区域，格式为(0, 0, 宽度, 高度)。
    示例：矩形 = 组件_取矩形2(某个wxPython组件)
    """
    return 组件.GetClientRect()

def 组件_取宽高(组件):
    """
    返回组件的实际宽高。

    :param 组件: wxPython中的组件。
    :return: 宽高，格式为(宽度, 高度)。
    示例：宽高 = 组件_取宽高(某个wxPython组件)
    """
    return 组件.GetClientSize()

def 组件_取宽高2(组件):
    """
    将组件的最佳大小合并为最小大小，然后返回结果。

    :param 组件: wxPython中的组件。
    :return: 宽高，格式为(宽度, 高度)。
    示例：宽高 = 组件_取宽高2(某个wxPython组件)
    """
    return 组件.GetEffectiveMinSize()

def 组件_取字体(组件):
    """
    返回组件的字体。

    :param 组件: wxPython中的组件。
    :return: 组件的字体。
    示例：字体 = 组件_取字体(某个wxPython组件)
    """
    return 组件.GetFont()

def 组件_取前景色(组件):
    """
    返回组件的前景色。

    :param 组件: wxPython中的组件。
    :return: 前景色。
    示例：前景色 = 组件_取前景色(某个wxPython组件)
    """
    return 组件.GetForegroundColour()

def 组件_取标记ID(组件):
    """
    返回组件的标识符。

    :param 组件: wxPython中的组件。
    :return: 组件的标识符。
    示例：标识符 = 组件_取标记ID(某个wxPython组件)
    """
    return 组件.GetId()

def 组件_取标题(组件):
    """
    返回组件的标题。

    :param 组件: wxPython中的组件。
    :return: 组件的标题。
    示例：标题 = 组件_取标题(某个wxPython组件)
    """
    return 组件.GetLabel()

def 组件_置工作区宽高(组件, 宽度, 高度):
    """
    设置组件工作区的宽高，不包含边框和标题栏的宽高。

    :param 组件: wxPython中的组件。
    :param 宽度: 工作区的宽度。
    :param 高度: 工作区的高度。
    :return: 无。
    示例：组件_置工作区宽高(某个wxPython组件, 800, 600)
    """
    return 组件.SetClientSize(宽度, 高度)

def 组件_取工作区最小宽高(组件):
    """
    返回组件工作区的最小大小。

    :param 组件: wxPython中的组件。
    :return: 工作区的最小大小。
    示例：最小宽高 = 组件_取工作区最小宽高(某个wxPython组件)
    """
    return 组件.GetMinClientSize()

def 组件_取最小宽高(组件):
    """
    返回组件的最小大小。

    :param 组件: wxPython中的组件。
    :return: 最小大小。
    示例：最小宽高 = 组件_取最小宽高(某个wxPython组件)
    """
    return 组件.GetMinSize()

def 组件_取组件名称(组件):
    """
    返回组件的名称。

    :param 组件: wxPython中的组件。
    :return: 组件的名称。
    示例：名称 = 组件_取组件名称(某个wxPython组件)
    """
    return 组件.GetName()

def 组件_取下一窗口(组件):
    """
    返回此组件之后的下一个同级窗口。

    :param 组件: wxPython中的组件。
    :return: 下一个同级窗口。
    示例：下一窗口 = 组件_取下一窗口(某个wxPython组件)
    """
    return 组件.GetNextSibling()

def 组件_取上一窗口(组件):
    """
    返回此组件之前的上一个同级窗口。

    :param 组件: wxPython中的组件。
    :return: 上一个同级窗口。
    示例：上一窗口 = 组件_取上一窗口(某个wxPython组件)
    """
    return 组件.GetPrevSibling()

def 组件_取父级窗口(组件):
    """
    返回组件的父级窗口。

    :param 组件: wxPython中的组件。
    :return: 父级窗口，如果没有父级则返回None。
    示例：父级窗口 = 组件_取父级窗口(某个wxPython组件)
    """
    return 组件.GetParent()

def 组件_弹出菜单(组件, 菜单, 左边, 顶边):
    """
    在指定位置显示一个弹出菜单。

    :param 组件: wxPython中的组件。
    :param 菜单: 要显示的弹出菜单。
    :param 左边: 弹出菜单的左边坐标。
    :param 顶边: 弹出菜单的顶边坐标。
    :return: 选中菜单项的ID。
    示例：选中项ID = 组件_弹出菜单(某个wxPython组件, 菜单, 100, 100)
    """
    return 组件.GetPopupMenuSelectionFromUser(菜单, 左边, 顶边)

def 组件_取左边顶边(组件):
    """
    获取组件相对于父窗口的位置。

    :param 组件: wxPython中的组件。
    :return: 组件位置，格式为(左边, 顶边)。
    示例：位置 = 组件_取左边顶边(某个wxPython组件)
    """
    return 组件.DirDialog()

def 组件_取窗口相对屏幕坐标(组件):
    """
    获取组件在屏幕坐标中的位置。

    :param 组件: wxPython中的组件。
    :return: 屏幕坐标中的位置，格式为(相对于屏幕的左边, 相对于屏幕的顶边)。
    示例：屏幕坐标 = 组件_取窗口相对屏幕坐标(某个wxPython组件)
    """
    return 组件.GetScreenPosition()

def 组件_取窗口相对屏幕矩形(组件):
    """
    获取组件在屏幕坐标中的矩形区域。

    :param 组件: wxPython中的组件。
    :return: 屏幕坐标中的矩形区域，格式为(相对于屏幕的左边, 相对于屏幕的顶边, 组件宽度, 组件高度)。
    示例：屏幕矩形 = 组件_取窗口相对屏幕矩形(某个wxPython组件)
    """
    return 组件.GetScreenRect()

def 组件_取内置滚动条位置(组件, 方向):
    """
    返回组件内置滚动条的位置。

    :param 组件: wxPython中的组件。
    :param 方向: 滚动条方向，4代表横向，8代表纵向。
    :return: 滚动条位置。
    示例：位置 = 组件_取内置滚动条位置(某个wxPython组件, 4)
    """
    return 组件.GetScrollPos(方向)

def 组件_取内置滚动条范围(组件, 方向):
    """
    返回组件内置滚动条的范围。

    :param 组件: wxPython中的组件。
    :param 方向: 滚动条方向，4代表横向，8代表纵向。
    :return: 滚动条范围。
    示例：范围 = 组件_取内置滚动条范围(某个wxPython组件, 4)
    """
    return 组件.GetScrollRange(方向)

def 组件_取内置滚动条缩略图大小(组件, 方向):
    """
    返回组件内置滚动条的缩略图大小。

    :param 组件: wxPython中的组件。
    :param 方向: 滚动条方向，4代表横向，8代表纵向。
    :return: 滚动条缩略图大小。
    示例：缩略图大小 = 组件_取内置滚动条缩略图大小(某个wxPython组件, 4)
    """
    return 组件.GetScrollThumb(方向)

def 组件_置滚动条位置(组件, 方向, 位置, 重绘):
    """
    设置组件内置滚动条的位置。

    :param 组件: wxPython中的组件。
    :param 方向: 滚动条方向，4代表横向，8代表纵向。
    :param 位置: 设置的滚动条位置。
    :param 重绘: 是否重绘，True或False。
    :return: 无。
    示例：组件_置滚动条位置(某个wxPython组件, 4, 20, True)
    """
    return 组件.SetScrollPos(方向, 位置, 重绘)

def 组件_置滚动条属性(组件, 方向, 位置, 可见大小, 最大位置, 重绘):
    """
    设置组件内置滚动条的属性。

    :param 组件: wxPython中的组件。
    :param 方向: 滚动条方向，4代表横向，8代表纵向。
    :param 位置: 滚动条位置。
    :param 可见大小: 滚动条可见部分大小。
    :param 最大位置: 滚动条最大位置。
    :param 重绘: 是否重绘，True或False。
    :return: 无。
    示例：组件_置滚动条属性(某个wxPython组件, 4, 0, 16, 50, True)
    """
    return 组件.SetScrollbar(方向, 位置, 可见大小, 最大位置, 重绘)

def 组件_取完整窗口宽高(组件):
    """
    返回组件整个窗口的大小，包括标题栏、边框、滚动条等。

    :param 组件: wxPython中的组件。
    :return: 整个窗口的大小，格式为(宽度, 高度)。
    示例：宽高 = 组件_取完整窗口宽高(某个wxPython组件)
    """
    return 组件.GetSize()

def 组件_是否使用系统主题设置背景(组件):
    """
    检查组件是否使用系统主题绘制其背景。

    :param 组件: wxPython中的组件。
    :return: True或False。
    示例：使用系统主题 = 组件_是否使用系统主题设置背景(某个wxPython组件)
    """
    return 组件.GetThemeEnabled()

def 组件_取顶级窗口(组件):
    """
    返回组件的顶级父窗口。

    :param 组件: wxPython中的组件。
    :return: 顶级父窗口。
    示例：顶级窗口 = 组件_取顶级窗口(某个wxPython组件)
    """
    return 组件.GetTopLevelParent()

def 组件_取虚拟宽高(组件):
    """
    返回组件的虚拟大小。

    :param 组件: wxPython中的组件。
    :return: 虚拟大小，格式为(宽度, 高度)。
    示例：虚拟宽高 = 组件_取虚拟宽高(某个wxPython组件)
    """
    return 组件.GetVirtualSize()

def 组件_是否有焦点(组件):
    """
    检查组件是否具有焦点。

    :param 组件: wxPython中的组件。
    :return: True或False。
    示例：有焦点 = 组件_是否有焦点(某个wxPython组件)
    """
    return 组件.HasFocus()

def 组件_是否有滚动条(组件, 方向):
    """
    检查组件是否具有指定方向的滚动条。

    :param 组件: wxPython中的组件。
    :param 方向: 滚动条方向，4代表横向，8代表纵向。
    :return: True或False。
    示例：有滚动条 = 组件_是否有滚动条(某个wxPython组件, 4)
    """
    return 组件.HasScrollbar(方向)

def 组件_是否透明(组件):
    """
    检查组件背景是否透明。

    :param 组件: wxPython中的组件。
    :return: True或False。
    示例：透明 = 组件_是否透明(某个wxPython组件)
    """
    return 组件.HasTransparentBackground()

def 组件_隐藏(组件):
    """
    隐藏指定组件。

    :param 组件: wxPython中的组件。
    :return: 无。
    示例：组件_隐藏(某个wxPython组件)
    """
    return 组件.Hide()

def 组件_隐藏带特效(组件, 效果, 效果时长):
    """
    使用特效隐藏组件。

    :param 组件: wxPython中的组件。
    :param 效果: 特效类型。
    :param 效果时长: 特效持续时间，单位毫秒。
    :return: 无。
    示例：组件_隐藏带特效(某个wxPython组件, 9, 500)
    """
    return 组件.HideWithEffect(效果, 效果时长)

def 组件_显示带特效(组件, 效果, 效果时长):
    """
    使用特效显示组件。

    :param 组件: wxPython中的组件。
    :param 效果: 特效类型。
    :param 效果时长: 特效持续时间，单位毫秒。
    :return: 无。
    示例：组件_显示带特效(某个wxPython组件, 9, 500)
    """
    return 组件.ShowWithEffect(效果, 效果时长)

def 组件_是否继承父级背景色(组件):
    """
    检查组件是否从其父级继承背景色。

    :param 组件: wxPython中的组件。
    :return: 如果此窗口从其父级继承背景色，则返回True。
    示例：继承背景色 = 组件_是否继承父级背景色(某个wxPython组件)
    """
    return 组件.InheritsBackgroundColour()

def 组件_是否继承父级前景色(组件):
    """
    检查组件是否从其父级继承前景色。

    :param 组件: wxPython中的组件。
    :return: 如果此窗口从其父级继承前景色，则返回True。
    示例：继承前景色 = 组件_是否继承父级前景色(某个wxPython组件)
    """
    return 组件.InheritsForegroundColour()

def 组件_重置缓存最佳大小(组件):
    """
    重置组件缓存的最佳大小值。

    :param 组件: wxPython中的组件。
    :return: 无。
    示例：组件_重置缓存最佳大小(某个wxPython组件)
    """
    return 组件.InvalidateBestSize()

def 组件_是否正在销毁(组件):
    """
    检查组件是否正在销毁过程中。

    :param 组件: wxPython中的组件。
    :return: 此窗口是否正在销毁中。
    示例：正在销毁 = 组件_是否正在销毁(某个wxPython组件)
    """
    return 组件.IsBeingDeleted()

def 组件_是否为下级窗口(组件, 对比组件):
    """
    检查指定的窗口是否是该窗口的后代。

    :param 组件: wxPython中的组件。
    :param 对比组件: 要对比的组件。
    :return: 如果指定的窗口是该窗口的后代（例如，子代或孙代或子孙等），则返回True。
    示例：是否为后代 = 组件_是否为下级窗口(某个wxPython组件, 另一个组件)
    """
    return 组件.IsDescendant(对比组件)

def 组件_是否禁用(组件):
    """
    检查组件是否被禁用。

    :param 组件: wxPython中的组件。
    :return: 如果组件被禁用（即不接受用户输入），则返回True。
    示例：是否禁用 = 组件_是否禁用(某个wxPython组件)
    """
    return 组件.IsEnabled()

def 组件_是否可获取焦点(组件):
    """
    检查组件是否可以获取焦点。

    :param 组件: wxPython中的组件。
    :return: 如果组件可以获取焦点，则返回True。
    示例：能否获取焦点 = 组件_是否可获取焦点(某个wxPython组件)
    """
    return 组件.IsFocusable()

def 组件_是否禁止重画(组件):
    """
    检查组件是否禁止重画。

    :param 组件: wxPython中的组件。
    :return: 如果组件已禁止重画，则返回True。
    示例：是否禁止重画 = 组件_是否禁止重画(某个wxPython组件)
    """
    return 组件.IsFrozen()

def 组件_是否始终显示滚动条(组件, 方向):
    """
    检查组件滚动条是否始终显示。

    :param 组件: wxPython中的组件。
    :param 方向: 滚动条的方向，4为横向滚动条，8为纵向滚动条。
    :return: 如果滚动条始终显示，则返回True。
    示例：始终显示滚动条 = 组件_是否始终显示滚动条(某个wxPython组件, 4)
    """
    return 组件.IsScrollbarAlwaysShown(方向)

def 组件_是否隐藏(组件):
    """
    检查组件是否已隐藏。

    :param 组件: wxPython中的组件。
    :return: 如果组件已调用命令隐藏（最小化、遮挡等不算隐藏），则返回True。
    示例：是否隐藏 = 组件_是否隐藏(某个wxPython组件)
    """
    return 组件.IsShown()

def 组件_是否显示在屏幕上(组件):
    """
    检查组件是否显示在屏幕上。

    :param 组件: wxPython中的组件。
    :return: 如果组件显示在屏幕上，则返回True。
    示例：是否显示在屏幕上 = 组件_是否显示在屏幕上(某个wxPython组件)
    """
    return 组件.IsShownOnScreen()

def 组件_是否启用(组件):
    """
    检查此窗口是否本质上已启用。

    :param 组件: wxPython中的组件。
    :return: 如果窗口启用，则返回True。
    示例：是否启用 = 组件_是否启用(某个wxPython组件)
    """
    return 组件.IsThisEnabled()

def 组件_是否为顶级窗口(组件):
    """
    检查窗口是否为顶级窗口。

    :param 组件: wxPython中的组件。
    :return: 如果是顶级窗口，则返回True。
    示例：是否顶级窗口 = 组件_是否为顶级窗口(某个wxPython组件)
    """
    return 组件.IsTopLevel()

def 组件_向下滚动(组件):
    """
    向下滚动窗口一行。

    :param 组件: wxPython中的组件。
    :return: 如果滚动了窗口，则返回True；如果窗口已在底部，则返回False。
    示例：向下滚动成功 = 组件_向下滚动(某个wxPython组件)
    """
    return 组件.LineDown()

def 组件_向上滚动(组件):
    """
    向上滚动窗口一行。

    :param 组件: wxPython中的组件。
    :return: 如果滚动了窗口，则返回True；如果窗口已在顶部，则返回False。
    示例：向上滚动成功 = 组件_向上滚动(某个wxPython组件)
    """
    return 组件.LineUp()

def 组件_滚动_页(组件, 滚动页数=1):
    """
    滚动窗口指定的页数。

    :param 组件: wxPython中的组件。
    :param 滚动页数: 向下滚动为正数，向上滚动为负数。
    :return: 如果滚动了窗口，则返回True。
    示例：滚动成功 = 组件_滚动_页(某个wxPython组件, 1)
    """
    return 组件.ScrollPages(滚动页数)

def 组件_滚动_行(组件, 滚动行数=1):
    """
    滚动窗口指定的行数。

    :param 组件: wxPython中的组件。
    :param 滚动行数: 向下滚动为正数，向上滚动为负数。
    :return: 如果滚动了窗口，则返回True。
    示例：滚动成功 = 组件_滚动_行(某个wxPython组件, 1)
    """
    return 组件.ScrollLines(滚动行数)

def 组件_移动左边顶边(组件, 左边, 顶边):
    """
    移动窗口到指定的左边和顶边位置。

    :param 组件: wxPython中的组件。
    :param 左边: 新的左边位置。
    :param 顶边: 新的顶边位置。
    :return: 无返回值。
    示例：组件_移动左边顶边(某个wxPython组件, 100, 100)
    """
    return 组件.Move(左边, 顶边)

def 组件_移动左边顶边2(组件, 左边, 顶边):
    """
    移动窗口到指定的左边和顶边位置。

    :param 组件: wxPython中的组件。
    :param 左边: 新的左边位置。
    :param 顶边: 新的顶边位置。
    :return: 无返回值。
    示例：组件_移动左边顶边2(某个wxPython组件, 100, 100)
    """
    return 组件.SetPosition((左边, 顶边))

def 组件_移动(组件, 左边=-1, 顶边=-1, 宽度=-1, 高度=-1):
    """
    移动并调整窗口大小。

    :param 组件: wxPython中的组件。
    :param 左边: 新的左边位置，不改变则为-1。
    :param 顶边: 新的顶边位置，不改变则为-1。
    :param 宽度: 新的宽度，不改变则为-1。
    :param 高度: 新的高度，不改变则为-1。
    :return: 无返回值。
    示例：组件_移动(某个wxPython组件, 100, 100, 500, 400)
    """
    return 组件.SetSize(左边, 顶边, 宽度, 高度)

def 组件_设置切换顺序_上(组件, 上一个组件):
    """
    设置当前组件在Tab键切换中的顺序。

    :param 组件: wxPython中的当前组件。
    :param 上一个组件: 当前组件在Tab键切换中的上一个组件。
    :return: 无返回值。
    示例：组件_设置切换顺序_上(某个wxPython组件, 上一个wxPython组件)
    """
    return 组件.MoveAfterInTabOrder(上一个组件)

def 组件_设置切换顺序_下(组件, 下一个组件):
    """
    设置当前组件在Tab键切换中的顺序。

    :param 组件: wxPython中的当前组件。
    :param 下一个组件: 当前组件在Tab键切换中的下一个组件。
    :return: 无返回值。
    示例：组件_设置切换顺序_下(某个wxPython组件, 下一个wxPython组件)
    """
    return 组件.MoveBeforeInTabOrder(下一个组件)

def 组件_生成组件ID(组件):
    """
    创建一个新的ID或当前未使用的ID范围。

    :param 组件: wxPython中的组件。
    :return: 新创建的ID，格式为负整数，例如：-31987。
    示例：新ID = 组件_生成组件ID(某个wxPython组件)
    """
    return 组件.NewControlId()

def 组件_重绘指定区域(组件, 矩形=(0, 0, 0, 0), 擦除背景=True):
    """
    重绘组件指定矩形的内容。

    :param 组件: wxPython中的组件。
    :param 矩形: 需要重绘的矩形区域。
    :param 擦除背景: 是否擦除背景。
    :return: 无返回值。
    示例：组件_重绘指定区域(某个wxPython组件, (10, 10, 100, 100))
    """
    return 组件.RefreshRect(矩形, 擦除背景)

def 组件_修改父级窗口(组件, 新父级组件):
    """
    修改组件的父级窗口。

    :param 组件: wxPython中的当前组件。
    :param 新父级组件: 新的父级组件。
    :return: 无返回值。
    示例：组件_修改父级窗口(某个wxPython组件, 新的父级组件)
    """
    return 组件.Reparent(新父级组件)

def 组件_桌面坐标转窗口内坐标(组件, x, y):
    """
    将屏幕坐标转换为组件内的坐标。

    :param 组件: wxPython中的组件。
    :param x: 屏幕上的x坐标。
    :param y: 屏幕上的y坐标。
    :return: 转换后的组件内坐标。
    示例：内坐标 = 组件_桌面坐标转窗口内坐标(某个wxPython组件, 100, 100)
    """
    return 组件.ScreenToClient(x, y)

def 组件_到最顶层(组件):
    """
    将组件提升到最顶层。

    :param 组件: wxPython中的组件。
    :return: 无返回值。
    示例：组件_到最顶层(某个wxPython组件)
    """
    return 组件.Raise()

def 组件_到最底层(组件):
    """
    将组件下降到最底层。

    :param 组件: wxPython中的组件。
    :return: 无返回值。
    示例：组件_到最底层(某个wxPython组件)
    """
    return 组件.Lower()

def 组件_是否已设置背景色(组件):
    """
    判断是否已为组件设置背景色。

    :param 组件: wxPython中的组件。
    :return: 如果已设置背景色，则返回True。
    示例：是否设置 = 组件_是否已设置背景色(某个wxPython组件)
    """
    return 组件.UseBackgroundColour()

def 组件_是否已设置前景色(组件):
    """
    判断是否已为组件设置前景色。

    :param 组件: wxPython中的组件。
    :return: 如果已设置前景色，则返回True。
    示例：是否设置 = 组件_是否已设置前景色(某个wxPython组件)
    """
    return 组件.UseForegroundColour()

def 组件_置背景颜色(组件, 颜色):
    """
    设置组件的背景色。

    :param 组件: wxPython中的组件。
    :param 颜色: 设置的颜色。
    :return: 无返回值。
    示例：组件_置背景颜色(某个wxPython组件, wx.Colour(255, 0, 0))
    """
    return 组件.SetBackgroundColour(颜色)

def 组件_单独置背景颜色(组件, 颜色):
    """
    设置窗口的背景色，但防止其被该窗口的子级继承。

    :param 组件: wxPython中的组件。
    :param 颜色: 设置的颜色。
    :return: 无返回值。
    示例：组件_单独置背景颜色(某个wxPython组件, wx.Colour(255, 255, 255))
    """
    return 组件.SetOwnBackgroundColour(颜色)

def 组件_置前景颜色(组件, 颜色):
    """
    设置组件的前景色。

    :param 组件: wxPython中的组件。
    :param 颜色: 设置的颜色。
    :return: 无返回值。
    示例：组件_置前景颜色(某个wxPython组件, wx.Colour(0, 0, 0))
    """
    return 组件.SetForegroundColour(颜色)

def 组件_单独置前景颜色(组件, 颜色):
    """
    设置窗口的前景色，但防止其被该窗口的子代继承。

    :param 组件: wxPython中的组件。
    :param 颜色: 设置的颜色。
    :return: 无返回值。
    示例：组件_单独置前景颜色(某个wxPython组件, wx.Colour(0, 0, 0))
    """
    return 组件.SetOwnForegroundColour(颜色)

def 组件_置标识ID(组件, ID):
    """
    设置组件的标识ID。

    :param 组件: wxPython中的组件。
    :param ID: 要设置的ID。
    :return: 无返回值。
    示例：组件_置标识ID(某个wxPython组件, 100)
    """
    return 组件.SetId(ID)

def 组件_置宽高(组件, 宽度, 高度):
    """
    设置组件的初始宽度和高度。

    :param 组件: wxPython中的组件。
    :param 宽度: 组件的宽度。
    :param 高度: 组件的高度。
    :return: 无返回值。
    示例：组件_置宽高(某个wxPython组件, 400, 300)
    """
    return 组件.SetInitialSize((宽度, 高度))

def 组件_置最大宽高(组件, 宽度, 高度):
    """
    设置整个窗口的最大尺寸范围。

    :param 组件: wxPython中的组件。
    :param 宽度: 窗口的最大宽度。
    :param 高度: 窗口的最大高度。
    :return: 无返回值。
    示例：组件_置最大宽高(某个wxPython组件, 800, 600)
    """
    return 组件.SetMaxSize((宽度, 高度))

def 组件_置最小宽高(组件, 宽度, 高度):
    """
    设置整个窗口的最小尺寸范围。

    :param 组件: wxPython中的组件。
    :param 宽度: 窗口的最小宽度。
    :param 高度: 窗口的最小高度。
    :return: 无返回值。
    示例：组件_置最小宽高(某个wxPython组件, 300, 200)
    """
    return 组件.SetMinSize((宽度, 高度))

def 组件_置工作区最大宽高(组件, 宽度, 高度):
    """
    设置窗口的最大客户端大小（不包含标题栏、菜单栏、状态栏的尺寸）。

    :param 组件: wxPython中的组件。
    :param 宽度: 客户端区域的最大宽度。
    :param 高度: 客户端区域的最大高度。
    :return: 无返回值。
    示例：组件_置工作区最大宽高(某个wxPython组件, 800, 600)
    """
    return 组件.SetMaxClientSize((宽度, 高度))

def 组件_置工作区最小宽高(组件, 宽度, 高度):
    """
    设置窗口的最小客户端大小（不包含标题栏、菜单栏、状态栏的尺寸）。

    :param 组件: wxPython中的组件。
    :param 宽度: 客户端区域的最小宽度。
    :param 高度: 客户端区域的最小高度。
    :return: 无返回值。
    示例：组件_置工作区最小宽高(某个wxPython组件, 300, 200)
    """
    return 组件.SetMinClientSize((宽度, 高度))

def 组件_置虚拟宽高(组件, 宽度, 高度):
    """
    设置窗口的虚拟大小（以像素为单位）。

    :param 组件: wxPython中的组件。
    :param 宽度: 虚拟宽度。
    :param 高度: 虚拟高度。
    :return: 无返回值。
    示例：组件_置虚拟宽高(某个wxPython组件, 1000, 800)
    """
    return 组件.SetVirtualSize((宽度, 高度))

def 组件_置标题(组件, 标题):
    """
    设置窗口的标题。

    :param 组件: wxPython中的组件。
    :param 标题: 要设置的标题文本。
    :return: 无返回值。
    示例：组件_置标题(某个wxPython组件, '新标题')
    """
    return 组件.SetLabel(标题)

def 组件_置名称(组件, 名称):
    """
    设置窗口的名称。

    :param 组件: wxPython中的组件。
    :param 名称: 要设置的名称。
    :return: 无返回值。
    示例：组件_置名称(某个wxPython组件, '新名称')
    """
    return 组件.SetName(名称)

def 组件_是否允许透明(组件):
    """
    判断窗口是否允许设置透明度。

    :param 组件: wxPython中的组件。
    :return: 如果允许透明返回True，否则返回False。
    示例：组件_是否允许透明(某个wxPython组件)
    """
    return 组件.CanSetTransparent()

def 组件_置透明度(组件, 透明度):
    """
    设置窗口的透明度。

    :param 组件: wxPython中的组件。
    :param 透明度: 透明度值，范围0-255（0为完全透明，255为完全不透明）。
    :return: 无返回值。
    示例：组件_置透明度(某个wxPython组件, 128)
    """
    return 组件.SetTransparent(透明度)

def 组件_置主题样式(组件, 样式):
    """
    设置窗口的主题样式。

    :param 组件: wxPython中的组件。
    :param 样式: 样式值，0为默认，1为跟随系统主题，更多样式请查阅wxPython文档。
    :return: 无返回值。
    示例：组件_置主题样式(某个wxPython组件, 1)
    """
    return 组件.SetBackgroundStyle(样式)

def 组件_置窗口样式(组件, 样式):
    """
    设置窗口的样式。

    :param 组件: wxPython中的组件。
    :param 样式: 窗口样式代码，如0表示无边框，更多样式请查阅wxPython文档。
    :return: 无返回值。
    示例：组件_置窗口样式(某个wxPython组件, 536870912)
    """
    return 组件.SetWindowStyleFlag(样式)

def 组件_刷新重绘(组件, 删除背景=False):
    """
    导致窗口及其所有子级重绘。

    :param 组件: wxPython中的组件。
    :param 删除背景: 是否删除背景，默认为False。
    :return: 无返回值。
    示例：组件_刷新重绘(某个wxPython组件, True)
    """
    return 组件.Refresh(删除背景)

def 组件_刷新重绘2(组件):
    """
    立即重绘窗口的无效区域及其所有子级。

    :param 组件: wxPython中的组件。
    :return: 无返回值。
    示例：组件_刷新重绘2(某个wxPython组件)
    """
    return 组件.Update()

def 组件_显示或隐藏(组件, 是否显示=True):
    """
    显示或隐藏窗口。

    :param 组件: wxPython中的组件。
    :param 是否显示: True显示，False隐藏。
    :return: 无返回值。
    示例：组件_显示或隐藏(某个wxPython组件, False)
    """
    return 组件.Show(是否显示)

def 组件_移动鼠标(组件, x, y):
    """
    将鼠标光标移动到组件上的指定位置。

    :param 组件: wxPython中的组件。
    :param x: 横坐标。
    :param y: 纵坐标。
    :return: 无返回值。
    示例：组件_移动鼠标(某个wxPython组件, 100, 100)
    """
    return 组件.WarpPointer(x, y)

def 组件_置鼠标光标样式(组件, 样式):
    """
    设置鼠标光标的样式。

    :param 组件: wxPython中的组件。
    :param 样式: 光标样式代码，参照wx.Cursor样式。
    :return: 无返回值。
    示例：组件_置鼠标光标样式(某个wxPython组件, 1)
    样式:
    0:无描述
    1:标准箭头光标。
    2:指向右侧的标准箭头光标。
    3:靶心光标。
    4:矩形字符光标。
    5:十字光标。
    6:手形光标。
    7:工字梁光标（垂直线）。
    8:表示鼠标左键按下。
    9:放大镜图标。
    10:表示按下中间按钮的鼠标。
    11:不可输入的符号光标。
    12:画笔光标。
    13:铅笔光标。
    14:指向左的光标。
    15:指向右的光标。
    16:箭头和问号。
    17:表示按下了右键的鼠标。
    18:调整大小的光标指向NE-SW。
    19:调整大小的光标指向N-S。
    20:调整大小的光标指向NW-SE。
    21:调整大小的光标指向W-E。
    22:一般大小的游标。
    23:Spraycan游标。
    24:等待光标。
    25:监视光标。
    26:透明光标。
    27:带有标准箭头的等待光标。
    28:无描述。
    """
    return 组件.SetCursor(wx.Cursor(样式))

def 组件_设置字体(组件, 字体名, 大小, 粗细, 下划线):
    """
    设置窗口组件的字体样式。

    :param 组件: wxPython中的组件。
    :param 字体名: 字体的名称。
    :param 大小: 字体大小。
    :param 粗细: 字体粗细，如wx.NORMAL, wx.BOLD。
    :param 下划线: 是否有下划线，True或False。
    :return: 无返回值。
    示例：组件_设置字体(某个wxPython组件, "Arial", 12, wx.BOLD, False)
    """
    return 组件.SetFont(wx.Font(大小, wx.DEFAULT, wx.NORMAL, 粗细, 下划线, 字体名))

def 程序_取指定坐标处组件(x, y):
    """
    获取桌面上指定坐标处的组件。

    :param x: 横坐标。
    :param y: 纵坐标。
    :return: 坐标处的wxPython组件。
    示例：程序_取指定坐标处组件(100, 100)
    """
    return wx.FindWindowAtPoint((x, y))

def 程序_取鼠标处组件跟坐标():
    """
    获取当前鼠标下面的组件及其坐标。

    :return: (组件, (x, y))，其中坐标是相对于桌面的坐标。
    示例：程序_取鼠标处组件跟坐标()
    """
    return wx.FindWindowAtPointer()

def 程序_取屏幕工作区矩形():
    """
    获取屏幕工作区的矩形尺寸（不包括任务栏）。

    :return: 工作区的矩形尺寸，格式：(0, 0, 宽度, 高度)。
    示例：程序_取屏幕工作区矩形()
    """
    return wx.GetClientDisplayRect()

def 程序_取屏幕分辨率():
    """
    获取屏幕的分辨率。

    :return: 屏幕分辨率，格式：(宽度, 高度)。
    示例：程序_取屏幕分辨率()
    """
    return wx.GetDisplaySize()

def 程序_取屏幕尺寸():
    """
    获取屏幕的尺寸（以毫米为单位）。

    :return: 屏幕尺寸，格式：(宽度mm, 高度mm)。
    示例：程序_取屏幕尺寸()
    """
    return wx.GetDisplaySizeMM()


def 程序_恢复默认鼠标光标() -> None:
    '对于应用程序中的所有窗口，将光标更改回原始光标'
    wx.EndBusyCursor()

def 程序_重置所有鼠标光标(光标类型: int) -> None:
    '''
    将光标更改为应用程序中所有窗口的给定光标
    光标类型:
    0:无描述
    1:标准箭头光标。
    2:指向右侧的标准箭头光标。
    3:靶心光标。
    4:矩形字符光标。
    5:十字光标。
    6:手形光标。
    7:工字梁光标（垂直线）。
    8:表示鼠标左键按下。
    9:放大镜图标。
    10:表示按下中间按钮的鼠标。
    11:不可输入的符号光标。
    12:画笔光标。
    13:铅笔光标。
    14:指向左的光标。
    15:指向右的光标。
    16:箭头和问号。
    17:表示按下了右键的鼠标。
    18:调整大小的光标指向NE-SW。
    19:调整大小的光标指向N-S。
    20:调整大小的光标指向NW-SE。
    21:调整大小的光标指向W-E。
    22:一般大小的游标。
    23:Spraycan游标。
    24:等待光标。
    25:监视光标。
    26:透明光标。
    27:带有标准箭头的等待光标。
    28:无描述。
    '''
    wx.BeginBusyCursor(wx.StockCursor(光标类型))

def 程序_关闭2() -> None:
    """
    立即结束程序。

    :return: None
    """
    wx.Abort()

def 程序_关闭() -> None:
    """
    立即结束程序，会卡顿下。

    :return: None
    """
    wx.Exit()

def 程序_系统错误代码转提示文本(code: int) -> str:
    """
    返回与给定系统错误代码对应的错误消息。

    :param code: int - 系统错误代码。
    :return: str - 对应的错误消息文本。
    """
    return wx.SysErrorMsgStr(code)

def 程序_电脑关机() -> None:
    """
    电脑关机。

    :return: None
    """
    wx.Shutdown(wx.SHUTDOWN_POWEROFF)

def 程序_电脑重启() -> None:
    """
    立即重启电脑，操作会卡顿下。

    :return: None
    """
    wx.Shutdown(wx.SHUTDOWN_REBOOT)

def 程序_延时_微秒(时间: int) -> None:
    """
    按微秒单位进行延时。1秒 = 1,000,000 微秒。

    :param 时间: int - 延时的时间，单位为微秒。
    :return: None
    """
    wx.MicroSleep(时间)

def 程序_延时_毫秒(时间: int) -> None:
    """
    按毫秒单位进行延时。1秒 = 1,000 毫秒。

    :param 时间: int - 延时的时间，单位为毫秒。
    :return: None
    """
    wx.MilliSleep(时间)

def 程序_延时_秒(时间: int) -> None:
    """
    按秒单位进行延时。

    :param 时间: int - 延时的时间，单位为秒。
    :return: None
    """
    wx.Sleep(时间)

def 程序_取本地英文时间() -> str:
    """
    返回当前的本地时间，格式为英文表示。

    :return: str - 当前的本地时间。
    """
    return wx.Now()

def 程序_取程序对象():
    """
    返回当前应用程序的对象。

    :return: 当前应用程序的对象。
    """
    return wx.GetApp()

def 程序_取程序顶级窗口列表() -> list:
    """
    返回应用程序顶级窗口的类似列表的对象。

    :return: 返回顶级窗口的对象列表。
    """
    return wx.GetTopLevelWindows()

def 程序_取计算机名() -> str:
    """
    返回计算机的名称。

    :return: 返回当前计算机的名称。
    """
    return wx.GetHostName()

def 程序_取系统版本信息() -> str:
    """
    返回系统版本信息。

    :return: 返回系统版本信息，例如 'Windows 10 (build 18363)，64位版'。
    """
    return wx.GetOsDescription()

def 程序_取系统用户名() -> str:
    """
    返回当前系统的用户名。

    :return: 返回系统的用户名，例如 'Administrator'。
    """
    return wx.GetUserName()

def 程序_系统是否64位() -> bool:
    """
    检查程序运行所在的操作系统是否为64位。

    :return: 如果操作系统是64位，则返回True，否则返回False。
    """
    return wx.IsPlatform64Bit()

def 程序_打开指定网址或目录(地址):
    """
    使用默认程序打开指定的网址或电脑目录。

    :param 地址: 网址或文件路径。
    :return: 成功打开返回True，否则返回False。
    示例：程序_打开指定网址或目录("https://www.example.com")
    """
    return wx.LaunchDefaultBrowser(地址)

def 程序_打开指定网址(url):
    """
    使用默认浏览器打开指定的网址。

    :param url: 网址。
    :return: 成功打开返回True，否则返回False。
    示例：程序_打开指定网址("https://www.example.com")
    """
    import webbrowser
    return webbrowser.open(url)

def 程序_取鼠标坐标():
    """
    获取当前鼠标的屏幕坐标。

    :return: 鼠标的屏幕坐标(x, y)。
    示例：程序_取鼠标坐标()
    """
    return wx.GetMouseState().GetPosition()

def 程序_鼠标侧键1是否按下():
    """
    检查鼠标侧键1是否被按下。

    :return: 如果鼠标侧键1被按下，返回True；否则返回False。
    示例：程序_鼠标侧键1是否按下()
    """
    return wx.GetMouseState().Aux1IsDown()

def 程序_鼠标侧键2是否按下():
    """
    检查鼠标侧键2是否被按下。

    :return: 如果鼠标侧键2被按下，返回True；否则返回False。
    示例：程序_鼠标侧键2是否按下()
    """
    return wx.GetMouseState().Aux2IsDown()

def 程序_鼠标左键是否按下():
    """
    检查鼠标左键是否被按下。

    :return: 如果鼠标左键被按下，返回True；否则返回False。
    示例：程序_鼠标左键是否按下()
    """
    return wx.GetMouseState().LeftIsDown()

def 程序_鼠标中键是否按下():
    """
    检查鼠标中键是否被按下。

    :return: 如果鼠标中键被按下，返回True；否则返回False。
    示例：程序_鼠标中键是否按下()
    """
    return wx.GetMouseState().MiddleIsDown()

def 程序_鼠标右键是否按下():
    """
    检查鼠标右键是否被按下。

    :return: 如果鼠标右键被按下，返回True；否则返回False。
    示例：程序_鼠标右键是否按下()
    """
    return wx.GetMouseState().RightIsDown()

def 程序_取当前进程ID():
    """
    获取当前程序的进程ID。

    :return: 当前程序的进程ID。
    示例：程序_取当前进程ID()
    """
    return wx.GetProcessId()

def 程序_系统环境是否支持中文():
    """
    检查系统环境是否支持中文。

    :return: 如果支持中文，返回True；否则返回False。
    示例：程序_系统环境是否支持中文()
    """
    return wx.GetLocale().IsAvailable(wx.LANGUAGE_CHINESE)

def 程序_取环境语言名称():
    """
    获取当前环境的语言名称。

    :return: 当前环境的语言名称，例如 "Chinese (Simplified)"。
    示例：程序_取环境语言名称()
    """
    return wx.GetLocale().GetLocale()

def 程序_取环境语言缩写():
    """
    获取当前环境的语言缩写。

    :return: 当前环境的语言缩写，例如 "zh_CN"。
    示例：程序_取环境语言缩写()
    """
    return wx.GetLocale().GetName()

def 程序_系统是否已激活():
    """
    检查系统是否已激活。

    :return: 如果系统已激活，返回True；否则返回False。
    示例：程序_系统是否已激活()
    """
    return wx.GetLibraryVersionInfo().HasCopyright()

def 程序_执行Dos(命令):
    """
    执行DOS命令。

    :param 命令: 要执行的DOS命令字符串。
    :return: 如果命令执行成功，返回True；否则返回False。
    示例：程序_执行Dos('echo Hello World')
    """
    return wx.Shell(命令)

def 组件_信息框(提示="", 标题="提示", 类型=0, 父窗口=None):
    """
    弹出不同类型的信息框。

    :param 提示: 信息框显示的文本内容。
    :param 标题: 信息框的标题。
    :param 类型: 信息框的类型。
    :param 父窗口: 信息框的父窗口。
    :return: 用户点击的按钮对应的返回值。
    示例：组件_信息框("操作成功", "提示", 0)
    类型:
    0.无图标信息框
    1.带取消键普通信息框
    2.带是/否键普通信息框
    3.带帮助键普通信息框
    4.带红色错误图标信息框
    5.带黄色感叹标题信息框
    6.带盾牌(类似权限验证)图标信息框

    返回值:2.是   4.确定   8.否   16.取消/关闭   4096.帮助
    """
    字典 = {0: wx.OK, 1: wx.OK | wx.CANCEL, 2: wx.YES_NO, 3: wx.OK | wx.HELP,
            4: wx.ICON_ERROR, 5: wx.ICON_EXCLAMATION, 6: wx.ICON_SHIELD}
    return wx.MessageBox(提示, 标题, 字典[类型], 父窗口)

def 组件_提示信息框(内容):
    """
    弹出带有蓝色反向感叹号图标的信息框。

    :param 内容: 信息框显示的文本内容。
    示例：组件_提示信息框("操作已完成")
    """
    return wx.LogMessage(内容)

def 组件_警告信息框(内容):
    """
    弹出带有黄色三角形感叹号图标的信息框。

    :param 内容: 信息框显示的文本内容。
    示例：组件_警告信息框("注意检查输入")
    """
    return wx.LogWarning(内容)

def 组件_报错信息框(内容):
    """
    弹出带有红叉图标的信息框。

    :param 内容: 信息框显示的文本内容。
    示例：组件_报错信息框("发生错误")
    """
    return wx.LogError(内容)

def 组件_文件选择器(标题="请选择文件", 初始路径="", 默认文件名="", 过滤器="所有文件|*.*", 父窗口=None):
    """
    弹出文件选择器对话框。

    :param 标题: 对话框的标题。
    :param 初始路径: 默认的初始路径。
    :param 默认文件名: 默认的文件名。
    :param 过滤器: 文件过滤器。
    :param 父窗口: 对话框的父窗口。
    :return: 用户选择的文件路径，未选择时返回空字符串。
    示例：组件_文件选择器()
    选择文件后返回完整文件路径,没选择返回空文本,可添加参数,flags(标识),parent(父窗口),x,y
    """
    return wx.FileSelector(标题, 初始路径, 默认文件名, wildcard=过滤器, parent=父窗口)

def 组件_保存文件对话框(提示="", 后缀="*", 默认文件名="", 父窗口=None):
    """
    弹出保存文件对话框。

    :param 提示: 对话框的提示文本。
    :param 后缀: 默认的文件后缀。
    :param 默认文件名: 默认的文件名。
    :param 父窗口: 对话框的父窗口。
    :return: 用户设置的文件路径，未选择时返回空字符串。
    示例：组件_保存文件对话框()
    """
    return wx.SaveFileSelector(提示, 后缀, 默认文件名, parent=父窗口)

def 组件_目录选择器(提示="", 初始路径="", 父窗口=None):
    """
    弹出目录选择对话框。

    :param 提示: 对话框的提示文本。
    :param 初始路径: 默认的初始路径。
    :param 父窗口: 对话框的父窗口。
    :return: 用户选择的目录路径，未选择时返回空字符串。
    示例：组件_目录选择器()
    """
    return wx.DirSelector(message=提示, default_path=初始路径, parent=父窗口)

def 组件_颜色选择器(初始颜色=None, 标题="请选择颜色", 父窗口=None):
    """
    弹出颜色选择对话框。

    :param 初始颜色: 默认的初始颜色。
    :param 标题: 对话框的标题。
    :param 父窗口: 对话框的父窗口。
    :return: 用户选择的颜色值，格式：(R, G, B, A)。
    示例：组件_颜色选择器()
    """
    return wx.GetColourFromUser(parent=父窗口, colInit=初始颜色, caption=标题)

def 组件_字体选择器(父窗口, 默认字体=None, 标题="请选择字体"):
    """
    弹出字体选择对话框。

    :param 父窗口: 对话框的父窗口。
    :param 默认字体: 默认的字体设置。
    :param 标题: 对话框的标题。
    :return: 用户选择的字体。
    示例：组件_字体选择器(None)
    """
    return wx.GetFontFromUser(parent=父窗口, fontInit=默认字体 if 默认字体 else 父窗口.GetFont(), caption=标题)

def 组件_数值对话框(标题="请设置数值", 提示="", 参数提示="", 默认值=1, 最小值=1, 最大值=100, 父窗口=None):
    """
    弹出一个设置数值的对话框。

    :param 标题: 对话框的标题。
    :param 提示: 对话框的提示文本。
    :param 参数提示: 对话框的参数提示。
    :param 默认值: 默认数值。
    :param 最小值: 数值的最小范围。
    :param 最大值: 数值的最大范围。
    :param 父窗口: 对话框的父窗口。
    :return: 用户输入的数值。
    示例：组件_数值对话框()
    """
    return wx.GetNumberFromUser(提示, 参数提示, 标题, 默认值, 最小值, 最大值, 父窗口)

def 组件_密码对话框(提示="", 标题="请输入密码", 默认文本="", 父窗口=None):
    """
    弹出一个密码输入对话框。

    :param 提示: 对话框的提示文本。
    :param 标题: 对话框的标题。
    :param 默认文本: 默认显示的文本。
    :param 父窗口: 对话框的父窗口。
    :return: 用户输入的密码文本，未输入时返回空字符串。
    示例：组件_密码对话框()
    """
    return wx.GetPasswordFromUser(message=提示, caption=标题, default_value=默认文本, parent=父窗口)

def 组件_单选列表对话框(提示="", 标题="请选择", 选择项=['未设置'], 初始选中=0, 父窗口=None):
    """
    弹出一个单选列表对话框。

    :param 提示: 对话框的提示文本。
    :param 标题: 对话框的标题。
    :param 选择项: 列表中的选项。
    :param 初始选中: 默认选中的选项索引。
    :param 父窗口: 对话框的父窗口。
    :return: 用户选择的选项文本，未选择时返回空字符串。
    示例：组件_单选列表对话框()
    """
    return wx.GetSingleChoice(message=提示, caption=标题, choices=选择项, initialSelection=初始选中, parent=父窗口)

def 组件_普通对话框(提示="", 标题="请输入", 默认文本='', 父窗口=None):
    """
    弹出一个普通文本输入对话框。

    :param 提示: 对话框的提示文本。
    :param 标题: 对话框的标题。
    :param 默认文本: 默认显示的文本。
    :param 父窗口: 对话框的父窗口。
    :return: 用户输入的文本，未输入时返回空字符串。
    示例：组件_普通对话框()
    """
    return wx.GetTextFromUser(message=提示, caption=标题, default_value=默认文本, parent=父窗口)

def 组件_气泡提示框(父窗口, 提示="", 标题="", 超时时间=3000, x=0, y=0):
    """
    弹出一个气泡提示框，默认在组件中间，可通过设置x,y调整。

    :param 父窗口: 气泡提示框的父窗口。
    :param 提示: 气泡提示框显示的提示文本。
    :param 标题: 气泡提示框的标题。
    :param 超时时间: 气泡提示框显示的持续时间，单位毫秒。
    :param x: 气泡提示框相对于父窗口的x坐标。
    :param y: 气泡提示框相对于父窗口的y坐标。
    :return: 无返回值。
    示例：组件_气泡提示框(父窗口, "这是一个提示", "提示标题")
    """
    气泡 = wx.adv.RichToolTip(标题, 提示)
    气泡.SetTimeout(超时时间)
    气泡.ShowFor(父窗口, (0, 0, x*2, y*2))

def 组件_系统弹窗(父窗口=None, 提示="", 标题=""):
    """
    电脑右下角弹出一个提示框，可以绑定提示框点击事件。

    :param 父窗口: 系统弹窗的父窗口。
    :param 提示: 系统弹窗显示的提示文本。
    :param 标题: 系统弹窗的标题。
    :return: 无返回值。
    示例：组件_系统弹窗(父窗口, "这是一个系统提示", "系统提示")
    电脑右下角弹出一个提示框,可以绑定提示框点击事件,详细操作：https://wxpython.org/Phoenix/docs/html/wx.adv.NotificationMessage.html#wx.adv.NotificationMessage.Show
    """
    提示框 = wx.adv.NotificationMessage(标题, 提示, 父窗口)
    提示框.Show()





# -*- coding: utf-8 -*-
class class_ec():

    def 绑定事件(self,事件,绑带函数):
        self.Bind(事件,绑带函数)

    @property
    def 窗口句柄(self):
        return self.GetHandle()

    @property
    def 组件名称(self):
        return self.GetName()

    @property
    def 标记ID(self):
        return self.GetId()

    @property
    def 左边顶边(self):
        return self.GetPosition()

    @property
    def 左边(self):
        return self.GetPosition()[0]

    @property
    def 顶边(self):
        return self.GetPosition()[1]

    @property
    def 宽度高度(self):
        return self.GetSize()

    @property
    def 宽度高度2(self):
        return self.GetClientSize()

    @property
    def 宽高3(self):
        '将窗口的最佳大小合并为最小大小'
        return self.GetEffectiveMinSize()

    @property
    def 宽度(self):
        return self.GetSize()[0]

    @property
    def 高度(self):
        return self.GetSize()[1]

    @property
    def 祖组件(self):
        return self.GetGrandParent()

    @property
    def 桌面相对坐标(self):
        "取组件左边跟顶边相对于桌面的坐标位置"
        return self.GetScreenPosition()

    @property
    def 桌面相对坐标2(self):
        "取组件左边跟顶边相对于桌面的坐标位置"
        return self.ClientToScreen(0, 0)

    @property
    def 窗口相对屏幕矩形(self):
        '出错返回False,返回窗口在屏幕坐标中的位置，无论该窗口是子窗口还是顶级窗口,格式:(相对于屏幕的左边,相对于屏幕的顶边,组件宽度,组件高度)'
        return self.GetScreenRect()

    @property
    def 背景颜色(self):
        '返回窗口的背景色,格式:(240, 240, 240, 255)'
        return self.GetBackgroundColour()

    @property
    def 可设置的最小尺寸(self):
        '返回窗口的最佳可接受最小尺寸, 返回格式: (宽度, 高度)，高度不包含标题栏高度'
        return self.GetBestSize()

    @property
    def 可设置的最大尺寸(self):
        '返回窗口的最佳可接受最大尺寸, 返回格式: (宽度, 高度)，高度不包含标题栏高度'
        return self.GetBestVirtualSize()

    @property
    def 主题样式(self):
        '样式：0.默认背景样式值,1.使用由系统或当前主题确定的默认背景,2.指示仅在用户定义的EVT_PAINT处理程序中擦除背景,3.无介绍,4.表示未擦除窗口背景，从而使父窗口得以显示'
        return self.GetBackgroundStyle()

    @property
    def 边框样式(self):
        return self.GetBorder()

    @property
    def 额外样式(self):
        return self.GetExtraStyle()

    @property
    def 字体及颜色(self):
        '返回: 字体,背景颜色,前景颜色，#(<wx._core.Font object at 0x000002140997DB88>, wx.Colour(240, 240, 240, 255), wx.Colour(0, 0, 0, 255))'
        结果 = self.GetClassDefaultAttributes()
        return 结果.font, 结果.colBg, 结果.colFg

    @property
    def 矩形(self):
        '返回窗口矩形：(左边,顶边,宽度,高度)'
        return self.GetRect()

    @property
    def 工作区矩形(self):
        return self.GetClientRect()

    @property
    def 字体(self):
        return self.GetFont()

    @property
    def 字体高度(self):
        '返回此窗口的字符高度'
        return self.GetCharHeight()

    @property
    def 字体平均宽度(self):
        '返回此窗口的平均字符宽度'
        return self.GetCharWidth()

    @property
    def 前景色(self):
        return self.GetForegroundColour()

    @property
    def 标签(self):
        return self.GetLabel()

    @property
    def 标题(self):
        return self.GetTitle()

    @property
    def 内容(self):
        return self.GetValue()

    @property
    def 工作区最小宽高(self):
        '返回窗口的工作区的最小大小，这向sizer布局机制指示这是其工作区的最小所需大小'
        return self.GetMinClientSize()

    @property
    def 最小宽高(self):
        '返回窗口的最小大小，这向sizer布局机制指示这是最小所需大小'
        return self.GetMinSize()

    @property
    def 下一个组件(self):
        '返回下一个组件的对象，即按TAB键切换到的下一个组件'
        return self.GetNextSibling()

    @property
    def 下上一个组件(self):
        '返回上一个组件的对象，即按TAB键切换到的上一个组件'
        return self.GetPrevSibling()

    @property
    def 父窗口(self):
        '返回父窗口对象'
        return self.GetParent()

    @property
    def 顶级窗口(self):
        return self.GetTopLevelParent()

    @property
    def 虚拟宽高(self):
        '这将获取窗口的虚拟大小,它返回窗口的客户端大小，但是在调用SetVirtualSize 它之后，将返回使用该方法设置的大小'
        return self.GetVirtualSize()

    def 取内置滚动条缩略图大小(self,方向):
        '返回内置滚动条的缩略图大小,方向：4.横向滚动条 8.纵向滚动条'
        return self.GetScrollThumb(方向)

    def 取内置滚动条范围(self,方向):
        '返回内置滚动条范围,方向：4.横向滚动条 8.纵向滚动条'
        return self.GetScrollRange(方向)

    def 取内置滚动条位置(self,方向):
        '返回内置滚动条的位置,方向：4.横向滚动条 8.纵向滚动条'
        return self.GetScrollPos(方向)

    @组件名称.setter
    def 组件名称(self, 名称):
        return self.SetName(名称)

    @标记ID.setter
    def 标记ID(self):
        return self.SetId()

    @左边顶边.setter
    def 左边顶边(self, 左边顶边):
        return self.Move(左边顶边[0], 左边顶边[1])

    def 置左边顶边(self, 左边, 顶边):
        return self.SetPosition(左边, 顶边)

    @左边.setter
    def 左边(self, 左边):
        return self.Move(左边, self.GetPosition()[1])

    @顶边.setter
    def 顶边(self, 顶边):
        return self.Move(self.GetPosition()[0], 顶边)

    @property
    def 左边2(self):
        return self.GetPosition()[0]

    @左边2.setter
    def 左边2(self, 左边):
        return self.SetPosition(左边, self.GetPosition()[1])

    @property
    def 顶边2(self):
        return self.GetPosition()[1]

    @顶边2.setter
    def 顶边2(self, 顶边):
        return self.SetPosition(self.GetPosition()[0], 顶边)

    @宽度高度.setter
    def 宽度高度(self, 宽度高度):
        return self.GetSize(宽度高度)

    @宽度高度2.setter
    def 宽度高度2(self, 宽度高度):
        return self.SetInitialSize(宽度高度)

    @宽度.setter
    def 宽度(self, 宽度):
        return self.SetInitialSize((宽度, self.GetSize()[1]))

    @高度.setter
    def 高度(self, 高度):
        return self.SetInitialSize((self.GetSize()[0], 高度))

    @标签.setter
    def 标签(self, 标签):
        return self.SetLabel(标签)

    @标题.setter
    def 标题(self, 标题):
        return self.SetTitle(标题)

    @内容.setter
    def 内容(self, 内容):
        return self.SetValue(内容)


    def 置拖放权限(self, 拖放=True):
        "设置是否允许接收拖放文件"
        return self.DragAcceptFiles(拖放)


    def 置工作区宽高(self, 宽度, 高度):
        '出设置组件工作区的宽高(不包含边框,标题栏的宽高)'
        return self.SetClientSize(宽度, 高度)

    @背景颜色.setter
    def 背景颜色(self, 颜色):
        return self.SetBackgroundColour(颜色)

    def 单独置背景颜色(self, 颜色):
        '设置窗口的背景色，但防止其被该窗口的子级继承'
        return self.SetOwnBackgroundColour(颜色)

    @property
    def 前景颜色(self):
        return self.GetForegroundColour()

    @前景颜色.setter
    def 前景颜色(self, 颜色):
        return self.SetForegroundColour(颜色)

    def 单独置前景颜色(self, 颜色):
        '设置窗口的前景色，但防止其被该窗口的子级继承'
        return self.SetOwnForegroundColour(颜色)

    @property
    def 最大宽高(self):
        return self.GetMaxSize()

    @最大宽高.setter
    def 最大宽高(self, 宽度高度):
        '设置整个窗口最大可设置的尺寸'
        return self.SetMaxSize(宽度高度)

    @最小宽高.setter
    def 最小宽高(self, 宽度高度):
        '设置整个窗口最小可设置的尺寸'
        return self.SetMinSize(宽度高度)

    @property
    def 工作区最大宽高(self):
        return self.GetMaxClientSize()

    @工作区最大宽高.setter
    def 工作区最大宽高(self, 宽度高度):
        '设置工作区最大可设置的尺寸'
        return self.SetMaxClientSize(宽度高度)

    @工作区最小宽高.setter
    def 工作区最小宽高(self, 宽度高度):
        '设置工作区最小可设置的尺寸'
        return self.SetMinClientSize(宽度高度)

    @虚拟宽高.setter
    def 虚拟宽高(self, 宽度高度):
        '设置窗口的虚拟大小（以像素为单位）'
        return self.SetVirtualSize(宽度高度)

    @property
    def 透明度(self):
        return self.GetTransparent()

    @透明度.setter
    def 透明度(self, 透明度):
        '设置窗口与透明度,范围0-255(0.完全透明,255完全不透明)'
        return self.SetTransparent(透明度)

    @主题样式.setter
    def 主题样式(self, 样式):
        '窗口样式:0.默认(可擦除背景),1.跟随系统主题,2.指示仅在用户定义的EVT_PAINT处理程序中擦除背景,3.表示未擦除窗口背景，从而使父窗口得以显示,4.无描述。'
        return self.SetBackgroundStyle(样式)

    @property
    def 窗口样式(self):
        return self.GetWindowStyleFlag()


    @窗口样式.setter
    def 窗口样式(self, 样式):
        return self.SetWindowStyleFlag(样式)

    @property
    def 鼠标样式(self):
        return self.GetCursor()

    @鼠标样式.setter
    def 鼠标样式(self, 样式):
        '''出错返回False,样式:
        0:无描述
        1:标准箭头光标。
        2:指向右侧的标准箭头光标。
        3:靶心光标。
        4:矩形字符光标。
        5:十字光标。
        6:手形光标。
        7:工字梁光标（垂直线）。
        8:表示鼠标左键按下。
        9:放大镜图标。
        10:表示按下中间按钮的鼠标。
        11:不可输入的符号光标。
        12:画笔光标。
        13:铅笔光标。
        14:指向左的光标。
        15:指向右的光标。
        16:箭头和问号。
        17:表示按下了右键的鼠标。
        18:调整大小的光标指向NE-SW。
        19:调整大小的光标指向N-S。
        20:调整大小的光标指向NW-SE。
        21:调整大小的光标指向W-E。
        22:一般大小的游标。
        23:Spraycan游标。
        24:等待光标。
        25:监视光标。
        26:透明光标。
        27:带有标准箭头的等待光标。
        28:无描述。
        '''
        return self.SetCursor(wx.Cursor(样式))

    @字体.setter
    def 字体(self, 字体):
        return self.SetFont(字体)


    def 置字体2(self, 字体名, 大小, 粗细, 下划线):
        return self.SetFont(wx.Font(大小, wx.DEFAULT, wx.NORMAL, 粗细, 下划线, 字体名))

    @property
    def 文本颜色(self):
        return self.GetForegroundColour()

    @文本颜色.setter
    def 文本颜色(self, 颜色):
        return self.SetForegroundColour(颜色)

    def 置组件顺序_上(self, 上一个组件):
        '设置使用TAB键切换组件时的切换顺序，从上一个组件按下TAB键后跳转到单前组件'
        return self.MoveAfterInTabOrder(上一个组件)

    def 置组件顺序_下(self, 下一个组件):
        '设置使用TAB键切换组件时的切换顺序，从在单前组件按下TAB键后切换到下一个组件'
        return self.MoveBeforeInTabOrder(下一个组件)

    def 置滚动条属性(self, 方向, 位置, 可见大小, 最大位置, 重绘):
        '''
        设置滚动条位置,方向可选4或8,重绘True或False(设置内置滚动条之一的位置)
        假设您希望使用相同的字体显示50行文本。窗口的大小设置为一次只能看到16行。您将使用：
        self.SetScrollbar(wx.VERTICAL, 0, 16, 50)
        '''
        return self.SetScrollbar(方向, 位置, 可见大小, 最大位置, 重绘)

    def 置滚动条位置(self, 方向, 位置, 重绘):
        '设置滚动条位置,方向可选4或8,重绘True或False(设置内置滚动条之一的位置)'
        return self.SetScrollPos(方向, 位置, 重绘)

    def 销毁(self):
        return self.Destroy()

    def 销毁2(self):
        '官方解释：计划在不久的将来销毁该窗口,每当销毁可能发生得太早时（例如，当该窗口或其子级仍在事件队列中等待时），都应使用此方法'
        return self.DestroyLater()

    def 销毁子窗口(self):
        return self.DestroyChildren()

    def 禁用2(self):
        return self.Disable()

    def 禁用(self, 禁用=True):
        "True为禁用组件，False为恢复组件使用"
        return self.Enable(not 禁用)

    def 禁止重画(self):
        return self.Freeze()

    def 允许重画(self):
        return self.Thaw()

    def 移动(self, 左边=-1, 顶边=-1, 宽度=-1, 高度=-1):
        '调整移动窗口的左边跟顶边位置并重新设置宽度跟高度,不想调整的填-1'
        return self.SetSize(左边, 顶边, 宽度, 高度)

    def 刷新重绘(self, 删除背景=False):
        '导致GTK1重新绘制此窗口及其所有子级（除非未实现此子级）'
        return self.Refresh(删除背景)

    def 刷新重绘2(self):
        '调用此方法将立即重新绘制窗口的无效区域及其所有子级的对象（通常仅在控制流返回事件循环时才发生）'
        return self.Update()

    def 遍历下级组件(self):
        '遍历组件下的子级组件,返回在WindowList 列表里'
        return self.GetChildren()

    def 弹出菜单(self, 菜单, 左边=0, 顶边=0):
        '此函数在此窗口中的给定位置显示一个弹出菜单，并返回所选的ID'
        return self.GetPopupMenuSelectionFromUser(菜单, 左边, 顶边)

    def 移动鼠标(self, x, y):
        '移动鼠标到组件内的指定位置'
        return self.WarpPointer(x, y)

    def 是否有焦点(self):
        return self.HasFocus()

    def 是否有滚动条(self, 方向):
        '返回此窗口当前是否具有该方向的滚动条,方向：4.横向滚动条 8.纵向滚动条'
        return self.HasScrollbar(方向)

    def 是否透明(self):
        return self.HasTransparentBackground()

    def 显示或隐藏(self, 是否显示=True):
        '显示或隐藏窗口'
        return self.Show(是否显示)

    def 隐藏(self):
        return self.Show(False)

    def 隐藏2(self):
        return self.Hide()

    def 隐藏_带特效(self, 效果, 效果时长):
        '''
        出错返回False,此功能可隐藏一个窗口并使用特殊的视觉效果
        效果：0.无效果，1.向左滚动窗口，2.向右滚动窗口，3.将窗口滚动到顶部，4.将窗口滚动到底部，5.向左滑动窗口，6.向右滑动窗口，7.将窗口滑动到顶部，8.将窗口滑动到底部，9.淡入或淡出效果，10.扩大或崩溃的作用
        效果时长：单位毫秒
        '''
        return self.HideWithEffect(效果, 效果时长)

    def 显示(self):
        return self.Show(True)

    def 显示_带特效(self, 效果, 效果时长):
        '''
        出错返回False,此功能可隐藏一个窗口并使用特殊的视觉效果
        效果：0.无效果，1.向左滚动窗口，2.向右滚动窗口，3.将窗口滚动到顶部，4.将窗口滚动到底部，5.向左滑动窗口，6.向右滑动窗口，7.将窗口滑动到顶部，8.将窗口滑动到底部，9.淡入或淡出效果，10.扩大或崩溃的作用
        效果时长：单位毫秒
        '''
        return self.ShowWithEffect(效果, 效果时长)

    def 是否继承父窗口背景色(self):
        return self.InheritsBackgroundColour()

    def 是否继承父窗口前景色(self):
        return self.InheritsForegroundColour()

    def 重置缓存最佳大小(self):
        '出错返回False,重置缓存的最佳大小值，以便下次需要时重新计算'
        return self.InvalidateBestSize()

    def 是否正在销毁(self):
        '出错返回False,此窗口是否正在销毁中'
        return self.IsBeingDeleted()

    def 是否禁用(self):
        return not self.IsEnabled()

    def 是否可获取焦点(self):
        return self.IsFocusable()

    def 是否为上级窗口(self, 待判断组件):
        return self.IsDescendant(待判断组件)

    def 是否禁止重画(self):
        return self.IsFrozen()

    def 是否隐藏(self):
        '判断是否调用命令隐藏了窗口,最小化,遮挡,不算隐藏'
        return self.IsShown()

    def 是否允许透明(self):
        return self.CanSetTransparent()

    def 是否显示在屏幕上(self):
        return self.IsShownOnScreen()

    def 是否启用(self):
        '是否从本质上启用了此窗口，False否则返回'
        return self.IsThisEnabled()

    def 是否为顶级窗口(self):
        return self.IsTopLevel()

    def 重绘指定区域(self, 矩形=(0, 0, 0, 0), 擦除背景=True):
        '重绘指定矩形的内容：仅对其内部的区域进行重绘'
        return self.RefreshRect(矩形, 擦除背景)

    def 修改父级窗口(self, 新父级组件):
        '即该窗口将从其当前父窗口中移除加入到新的父级窗口下'
        return self.Reparent(新父级组件)

    def 桌面坐标转窗口内坐标(self, x, y):
        '从屏幕转换为客户端窗口内工作区坐标,'
        return self.ScreenToClient(x, y)

    def 到最顶层(self):
        '调整显示顺序'
        self.Raise()

    def 到最底层(self):
        '调整显示顺序'
        self.Lower()

    def 是否已设置背景色(self):
        return self.UseBackgroundColour()

    def 是否已设置前景色(self):
        return self.UseForegroundColour()

    def 向上滚动(self):
        '与ScrollLines （-1）相同,返回True是否滚动窗口，False如果窗口已经在顶部，则什么也不做'
        return self.LineUp()

    def 向下滚动(self):
        '与ScrollLines （1）相同，返回True是否滚动窗口，False如果窗口已经在底部，则什么也不做'
        return self.LineDown()

    def 是否始终显示滚动条(self, 方向):
        '判断滚动条是否始终显示,方向：4.横向滚动条 8.纵向滚动条'
        return self.IsScrollbarAlwaysShown(方向)

    def 滚动_页(self, 滚动页数=1):
        '滚动页数:向上滚动1次为-1,向下为1'
        return self.ScrollPages(滚动页数)

    def 滚动_行(self, 滚动行数=1):
        '出错返回False,滚动行数:向上滚动1次为-1,向下为1'
        return self.ScrollLines(滚动行数)

    def 是否使用系统主题设置背景(self):
        '窗口是否使用系统主题绘制其背景'
        return self.GetThemeEnabled()


class wx_Frame(wx.Frame, class_ec):

    @property
    def 标题(self):
        return self.GetTitle()

    @标题.setter
    def 标题(self, value):
        self.SetTitle(value)

    def 关闭(self):
        self.Close(True)

    def 置图标(self, 图标路径):
        icon = wx.Icon(图标路径)
        self.SetIcon(icon)

    def 居中(self):
        '将窗口调整到屏幕中间'
        self.Centre()

    def 创建状态栏(self, 项目, 抓取器=True):
        "创建状态栏，项目格式为[(项目名, 宽度), ...]"
        # 之前的实现代码

    # 省略其他已有的方法

    @property
    def 状态栏项目数(self):
        return self.状态栏.GetFieldsCount()

    @状态栏项目数.setter
    def 状态栏项目数(self, 项目数):
        宽度列表 = [-1 for _ in range(项目数)]
        self.状态栏.SetFieldsCount(项目数, 宽度列表)



class wx_Button(wx.Button, class_ec):

    @property
    def 认证图标显示(self):
        # 这里需要一个方法来检测当前认证图标的状态
        # 但wxPython的Button类并没有提供直接的方法来检测这一状态
        # 因此，这个属性可能需要根据实际情况进行调整
        pass

    @认证图标显示.setter
    def 认证图标显示(self, 显示=True):
        self.SetAuthNeeded(显示)

    def 置顶层默认项(self):
        '设置后再窗口中按回车即可触发按钮点击事件'
        self.SetDefault()

#标签
class wx_StaticText(wx.StaticText,class_ec):
    pass

#编辑框
class wx_TextCtrl(wx.TextCtrl, class_ec):

    def 取新文本样式(self):
        '返回当前用于新文本的样式。'
        return self.GetDefaultStyle()

    def 取指定行长度(self, 行号):
        '获取指定行的长度，不包括任何尾随换行符。'
        return self.GetLineLength(行号)

    def 取指定行内容(self, 行号):
        '返回文本控件中给定行的内容，不包括任何结尾的换行符。'
        return self.GetLineText(行号)

    def 取缓冲区行数(self):
        return self.GetNumberOfLines()

    def 内容是否被修改(self):
        '返回True文本是否已被用户修改。调用SetValue不会使控件修改。'
        return self.IsModified()

    def 是否为多行编辑框(self):
        return self.IsMultiLine()

    def 是否为单行编辑框(self):
        return self.IsSingleLine()

    def 载入指定文件内容(self, 路径):
        '从指定文件加载内容到编辑框'
        return self.LoadFile(路径)

    def 内容写到指定文件(self, 路径):
        '将编辑框的内容写到指定文件内'
        return self.SaveFile(路径)

    def 标记为已修改2(self):
        '将文本标记为已修改'
        return self.MarkDirty()

    def 指定位置转像素位置(self, 位置):
        '取指定位置处的文本的像素坐标'
        return self.PositionToCoords(位置)

    def 指定位置转行列位置(self, 位置):
        '取指定位置处的文本所在行跟列,返回一个元组,(是否存在,行,列)'
        return self.PositionToXY(位置)

    def 置新文本样式(self, 样式):
        '更改要用于要添加到控件的新文本的默认样式。'
        return self.SetDefaultStyle(样式)

    def 置修改状态(self, 修改=True):
        '将控件标记为是否被用户修改'
        return self.SetModified(修改)

    def 置指定范围样式(self, 开始位置, 结束位置, 样式):
        return self.SetStyle(开始位置, 结束位置, 样式)

    def 置指定位置可见(self, 位置):
        '使指定位置的字符显示在编辑框可见范围内'
        return self.ShowPosition(位置)

    def 指定行列转位置(self, 行, 列):
        '将给定的从零开始的列和行号转换为位置'
        return self.XYToPosition(行, 列)

    def 加入文本(self, 内容):
        return self.write(内容)

    def 清空内容(self):
        self.Clear()

#单选框
class wx_RadioButton(wx.RadioButton, class_ec):

    @property
    def 选中(self):
        """
        获取单选框的选中状态。
        返回True表示选中，返回False表示未选中。
        """
        return self.GetValue()

    @选中.setter
    def 选中(self, 状态):
        """
        设置单选框的选中状态。
        :param 状态: True表示选中，False表示未选中。
        """
        self.SetValue(状态)

#多选框
class wx_CheckBox(wx.CheckBox, class_ec):

    @property
    def 选中(self):
        """
        获取复选框的选中状态。
        返回True表示选中，返回False表示未选中。
        """
        return self.GetValue()

    @选中.setter
    def 选中(self, 状态):
        """
        设置复选框的选中状态。
        :param 状态: True表示选中，False表示未选中。
        """
        self.SetValue(状态)

    @property
    def 三态状态(self):
        """
        获取三态复选框的当前状态。
        返回 0.未选中  1.选中  2.半选中
        """
        return self.Get3StateValue()

    @三态状态.setter
    def 三态状态(self, 状态):
        """
        设置三态复选框的状态。
        :param 状态: 0.未选中  1.选中  2.半选中
        """
        self.Set3StateValue(状态)

    def 是否为三态复选框(self):
        return self.Is3State()

    def 是否可设置为半选中(self):
        return self.Is3rdStateAllowedForUser()

#图片框
class wx_StaticBitmap(wx.StaticBitmap, class_ec):

    @property
    def 图片(self):
        """
        获取控件中当前使用的位图。
        """
        return self.GetBitmap()

    @图片.setter
    def 图片(self, 图片):
        """
        设置控件中要显示的位图。
        :param 图片: 要设置的位图对象。
        """
        self.SetBitmap(图片)

    @property
    def 图标(self):
        """
        获取控件中当前使用的图标。
        """
        return self.GetIcon()

    @图标.setter
    def 图标(self, 图标):
        """
        设置控件中要显示的图标。
        :param 图标: 要设置的图标对象。
        """
        self.SetIcon(图标)

    @property
    def 缩放模式(self):
        """
        获取控件的缩放模式。
        返回值：0.以原始大小显示 1.比例填充 2.保持纵横比缩放 3.填充控件大小。
        """
        return self.GetScaleMode()

    @缩放模式.setter
    def 缩放模式(self, 模式):
        """
        设置控件的缩放模式。
        :param 模式: 0.以原始大小显示 1.比例填充 2.保持纵横比缩放 3.填充控件大小。
        """
        self.SetScaleMode(模式)

#组合框
class wx_ComboBox(wx.ComboBox, class_ec):

    @property
    def 取项目数(self):
        """
        获取组合框中的项目数量。
        """
        return self.GetCount()

    @property
    def 现行选中项(self):
        """
        获取当前选中的项目索引。
        """
        return self.GetCurrentSelection()

    @现行选中项.setter
    def 现行选中项(self, 索引):
        """
        设置当前选中的项目索引。
        :param 索引: 要选中的项目索引。
        """
        self.SetSelection(索引)

    @property
    def 选中项文本(self):
        """
        获取当前选中的项目文本。
        """
        return self.GetStringSelection()

    @选中项文本.setter
    def 选中项文本(self, 项目文本):
        """
        设置当前选中的项目文本。
        :param 项目文本: 要选中的项目文本。
        """
        self.SetStringSelection(项目文本)

    @property
    def 默认文本(self):
        """
        获取或设置组合框的默认文本。
        """
        return self.GetValue()

    @默认文本.setter
    def 默认文本(self, 文本):
        """
        设置组合框的默认文本。
        :param 文本: 要设置的默认文本。
        """
        self.SetValue(文本)

    def 取指定项目索引(self, 项目文本, 是否区分大小写=False):
        return self.FindString(项目文本, 是否区分大小写)

    def 取选中范围(self):
        return self.GetTextSelection()

    def 取指定项目文本(self, 索引):
        return self.GetString(索引)

    def 列表项是否为空(self):
        return self.IsListEmpty()

    def 弹出列表(self):
        self.Popup()

    def 置指定项目文本(self, 索引, 文本):
        self.SetString(索引, 文本)

    def 置选中项(self, 索引):
        self.SetSelection(索引)

    def 选中范围文本(self, 开始位置, 结束位置):
        '如果两个参数都等于-1，则选择控件中的所有文本'
        self.SetTextSelection(开始位置, 结束位置)

    def 清空表项(self):
        self.Clear()

    def 置项目列表(self, 项目列表):
        '会覆盖原有的项目列表'
        self.SetItems(项目列表)

    def 加入项目(self, 项目):
        '支持单个或多个项目,多个项目使用列表传入，加入后会返回最后一个项目索引'
        return self.Append(项目)

    def 加入项目2(self, 项目):
        '支持单个或多个项目,多个项目使用列表传入'
        self.AppendItems(项目)

    def 删除指定项目(self, 索引):
        self.Delete(索引)

    def 插入项目(self, 插入位置, 项目列表):
        return self.Insert(项目列表, 插入位置)

#进度条
class wx_Gauge(wx.Gauge, class_ec):

    @property
    def 最大位置(self):
        """
        获取进度条的最大位置。
        """
        return self.GetRange()

    @最大位置.setter
    def 最大位置(self, 位置):
        """
        设置进度条的最大位置。
        :param 位置: 进度条的最大位置值。
        """
        self.SetRange(位置)

    @property
    def 当前位置(self):
        """
        获取进度条的当前位置。
        """
        return self.GetValue()

    @当前位置.setter
    def 当前位置(self, 位置):
        """
        设置进度条的当前位置。
        :param 位置: 进度条的当前位置值。
        """
        self.SetValue(位置)

    @property
    def 是否为垂直进度条(self):
        """
        判断进度条是否为垂直方向。
        :return: True 如果进度条是垂直的，否则 False。
        """
        return self.IsVertical()

    def 置加载模式(self):
        """
        启动进度条的加载模式，使其呈现滚动加载的视觉效果,调用SetValue停止滚动加载。
        """
        self.Pulse()

#滑块条
class wx_Slider(wx.Slider, class_ec):

    def 清除刻度线(self):
        self.ClearTicks()

    @property
    def 行大小(self):
        return self.GetLineSize()

    @行大小.setter
    def 行大小(self, 数值):
        self.SetLineSize(数值)

    @property
    def 最大位置(self):
        return self.GetMax()

    @最大位置.setter
    def 最大位置(self, 数值):
        self.SetMax(数值)

    @property
    def 最小位置(self):
        return self.GetMin()

    @最小位置.setter
    def 最小位置(self, 数值):
        self.SetMin(数值)

    @property
    def 页面间隔(self):
        return self.GetPageSize()

    @页面间隔.setter
    def 页面间隔(self, 数值):
        self.SetPageSize(数值)

    @property
    def 滑块数值范围(self):
        return self.GetRange()

    @滑块数值范围.setter
    def 滑块数值范围(self, 范围):
        '''
        :param 范围: 如(1,100)
        :return:
        '''
        self.SetRange(范围[0], 范围[1])

    @property
    def 选中终点(self):
        return self.GetSelEnd()

    @选中终点.setter
    def 选中终点(self, 值):
        self.SetSelection(self.选中起点, 值)

    @property
    def 选中起点(self):
        return self.GetSelStart()

    @选中起点.setter
    def 选中起点(self, 值):
        self.SetSelection(值, self.选中终点)

    @property
    def 滑块大小(self):
        return self.GetThumbLength()

    @滑块大小.setter
    def 滑块大小(self, 数值):
        self.SetThumbLength(数值)

    @property
    def 刻线间隔(self):
        return self.GetTickFreq()

    @刻线间隔.setter
    def 刻线间隔(self, 间隔):
        self.SetTickFreq(间隔)

    @property
    def 滑块位置(self):
        return self.GetValue()

    @滑块位置.setter
    def 滑块位置(self, 位置):
        self.SetValue(位置)

    def 置刻线位置(self, 位置):
        self.SetTick(位置)

#整数微调框
class wx_SpinCtrl(wx.SpinCtrl, class_ec):

    @property
    def 数值进制类型(self):
        """返回10或16，十进制或16进制"""
        return self.GetBase()

    @数值进制类型.setter
    def 数值进制类型(self, 类型):
        """类型：10或16，十进制或16进制"""
        self.SetBase(类型)

    @property
    def 最大值(self):
        return self.GetMax()

    @最大值.setter
    def 最大值(self, 数值):
        self.SetMax(数值)

    @property
    def 最小值(self):
        return self.GetMin()

    @最小值.setter
    def 最小值(self, 数值):
        self.SetMin(数值)

    @property
    def 数值范围(self):
        """获取微调的数值范围"""
        return self.GetRange()

    @数值范围.setter
    def 数值范围(self, 范围):
        """
        :param 范围: (1,100)
        :return:
        """
        self.SetRange(范围[0], 范围[1])

    @property
    def 当前数值(self):
        return self.GetValue()

    @当前数值.setter
    def 当前数值(self, 数值):
        self.SetValue(数值)

#动画框
class wx_adv_AnimationCtrl(wx.adv.AnimationCtrl, class_ec):

    def 创建控件动画对象(self):
        return self.CreateCompatibleAnimation()

    def 创建控件动画对象2(self):
        return self.CreateAnimation()

    @property
    def 当前动画(self):
        return self.GetAnimation()

    @property
    def 当前图片(self):
        """返回当此控件显示的非活动位图；查看SetInactiveBitmap 更多信息"""
        return self.GetInactiveBitmap()

    @property
    def 是否正在播放动画(self):
        return self.IsPlaying()

    def 载入动画_流(self, 文件):
        """从给定的流中加载动画并调用SetAnimation"""
        return self.Load(文件)

    def 载入动画_文件(self, 文件):
        """从给定的文件加载动画并调用SetAnimation。"""
        return self.LoadFile(文件)

    def 播放动画(self):
        return self.Play()

    def 停止播放(self):
        return self.Stop()

    def 载入动画(self, 动画):
        """设置动画在此控件中播放"""
        return self.SetAnimation(动画)

    def 置默认显示图片(self, 图片):
        """设置位图在不播放动画时显示在控件上。"""
        return self.SetInactiveBitmap(图片)

#列表框
class wx_ListBox(wx.ListBox, class_ec):

    def 取消指定选中项(self, 索引):
        """在列表框中取消选择一个项目。"""
        return self.Deselect(索引)

    def 保证显示(self, 索引):
        """确保当前显示具有给定索引的项目。"""
        return self.EnsureVisible(索引)

    def 取指定项目索引(self, 查找的内容, 区分大小写=False):
        """查找标签与给定字符串匹配的项目。返回项目索引"""
        return self.FindString(查找的内容, 区分大小写)

    @property
    def 项目数(self):
        return self.GetCount()

    @property
    def 可见项目数(self):
        """返回可以垂直放入列表框可见区域的项目数。"""
        return self.GetCountPerPage()

    @property
    def 选中项索引(self):
        return self.GetSelection()

    @property
    def 选中范围索引(self):
        """返回一个列表包含所有选中项索引,用当前所选项目的位置填充一个整数数组。"""
        return self.GetSelections()

    def 取指定项目文本(self, 索引):
        return self.GetString(索引)

    @property
    def 首个可见项索引(self):
        """返回最顶部可见项目的索引。"""
        return self.GetTopItem()

    def 取指定坐标索引(self, 左边, 顶边):
        """返回列表框内指定坐标处项目索引"""
        return self.HitTest(左边, 顶边)

    def 插入项目(self, 插入位置, 项目列表):
        return self.InsertItems(项目列表, 插入位置)

    def 清空表项(self):
        self.Clear()

    def 置项目列表(self, 项目列表):
        """会覆盖原有的项目列表"""
        self.SetItems(项目列表)

    def 加入项目(self, 项目):
        """支持单个或多个项目,多个项目使用列表传入，加入后会返回最后一个项目索引"""
        return self.Append(项目)

    def 加入项目2(self, 项目):
        """支持单个或多个项目,多个项目使用列表传入"""
        self.AppendItems(项目)

    def 删除指定项目(self, 索引):
        self.Delete(索引)

    def 项目是否选中(self, 索引):
        return self.IsSelected(索引)

    def 表项是否按字母排序(self):
        return self.IsSorted()

    def 置顶指定项(self, 索引):
        """将指定的项目设置为第一个可见项目。"""
        self.SetFirstItem(索引)

    def 置指定项目背景色(self, 索引, 颜色):
        """在列表框中设置项目的背景色。仅在MSW上且wx.LB_OWNERDRAW设置了标志时有效。"""
        self.SetItemBackgroundColour(索引, 颜色)
        self.Refresh()

    def 置指定项目前景色(self, 索引, 颜色):
        """在列表框中设置项目的前景色。仅在MSW上且wx.LB_OWNERDRAW设置了标志时有效。"""
        self.SetItemForegroundColour(索引, 颜色)
        self.Refresh()

    def 置指定项目字体(self, 索引, 字体):
        """在列表框中设置项目的字体。仅在MSW上且wx.LB_OWNERDRAW设置了标志时有效。"""
        self.SetItemFont(索引, 字体)
        self.Refresh()

    def 置指定项目文本(self, 索引, 文本):
        self.SetString(索引, 文本)

    def 置现行选中项_文本(self, 项目文本):
        return self.SetStringSelection(项目文本)

    def 置现行选中项(self, 索引):
        return self.SetSelection(索引)

    @property
    def 选中项文本(self):
        return self.GetStringSelection()

#选择列表框
class wx_CheckListBox(wx.CheckListBox, class_ec):

    def 置选中状态(self, 索引, 选中=True):
        self.Check(索引, 选中)

    def 选中项目(self, 索引):
        self.Check(索引, True)

    def 取消选中项目(self, 索引):
        self.Check(索引, False)

    @property
    def 项目数(self):
        return self.GetCount()

    @property
    def 选中项(self):
        """返回一个元组,包含所有选中的表项索引"""
        return self.GetCheckedItems()

    @property
    def 选中项_文本(self):
        """返回一个元组,包含所有选中的表项文本"""
        return self.GetCheckedStrings()

    def 是否选中(self, 索引):
        return self.IsChecked(索引)

    def 置选中状态_批量(self, 索引列表):
        """传入需要选中的索引列表,不存在的会报错"""
        self.SetCheckedItems(索引列表)

    def 置选中状态_文本_批量(self, 文本列表):
        """传入需要选中的项目文本列表,不存在的会报错"""
        self.SetCheckedStrings(文本列表)

    def 置指定项目背景色(self, 索引, 颜色):
        """在列表框中设置项目的背景色。仅在MSW上且wx.LB_OWNERDRAW设置了标志时有效。"""
        self.SetItemBackgroundColour(索引, 颜色)
        self.Refresh()

    def 置指定项目前景色(self, 索引, 颜色):
        """在列表框中设置项目的前景色。仅在MSW上且wx.LB_OWNERDRAW设置了标志时有效。"""
        self.SetItemForegroundColour(索引, 颜色)
        self.Refresh()

    def 置指定项目字体(self, 索引, 字体):
        """在列表框中设置项目的字体。仅在MSW上且wx.LB_OWNERDRAW设置了标志时有效。"""
        self.SetItemFont(索引, 字体)
        self.Refresh()

    def 置顶指定项(self, 索引):
        """将指定的项目设置为第一个可见项目。"""
        self.SetFirstItem(索引)

    @property
    def 首个可见项索引(self):
        """返回最顶部可见项目的索引。"""
        return self.GetTopItem()

    def 取指定坐标索引(self, 左边, 顶边):
        """返回列表框内指定坐标处项目索引"""
        return self.HitTest(左边, 顶边)

    def 插入项目(self, 插入位置, 项目列表):
        return self.Insert(项目列表, 插入位置)

    def 插入项目2(self, 插入位置, 项目列表):
        return self.InsertItems(项目列表, 插入位置)

    def 清空表项(self):
        self.Clear()

    def 置项目列表(self, 项目列表):
        """会覆盖原有的项目列表"""
        self.SetItems(项目列表)

    def 加入项目(self, 项目):
        """支持单个或多个项目,多个项目使用列表传入，加入后会返回最后一个项目索引"""
        return self.Append(项目)

    def 加入项目2(self, 项目):
        """支持单个或多个项目,多个项目使用列表传入"""
        self.AppendItems(项目)

    def 删除指定项目(self, 索引):
        self.Delete(索引)

#图形按钮
class wx_BitmapButton(wx.BitmapButton,class_ec):
    pass

#超级链接框
class wx_adv_HyperlinkCtrl(wx.adv.HyperlinkCtrl, class_ec):

    @property
    def 单击前焦点颜色(self):
        """返回鼠标悬停在控件上时用于打印超链接标签的颜色。"""
        return self.GetHoverColour()

    @单击前焦点颜色.setter
    def 单击前焦点颜色(self, 颜色):
        """设置鼠标悬停在控件上时用于打印超链接标签的颜色。"""
        self.SetHoverColour(颜色)

    @property
    def 初始颜色(self):
        """返回以前从未单击过链接（即尚未访问链接）并且鼠标不在控件上时用于打印标签的颜色。"""
        return self.GetNormalColour()

    @初始颜色.setter
    def 初始颜色(self, 颜色):
        """设置以前从未单击过链接（即未访问链接）并且鼠标不在控件上时用于打印标签的颜色。"""
        self.SetNormalColour(颜色)

    @property
    def URL(self):
        """返回与超链接关联的URL。"""
        return self.GetURL()

    @URL.setter
    def URL(self, url):
        """设置与超链接关联的URL。"""
        self.SetURL(url)

    @property
    def 是否已点击(self):
        """返回True超链接是否已被用户至少单击一次。"""
        return self.GetVisited()

    @是否已点击.setter
    def 是否已点击(self, 已访问):
        """将超链接标记为已访问/未访问"""
        self.SetVisited(已访问)

    @property
    def 单击后焦点颜色(self):
        """返回鼠标悬停在控件上且之前已单击链接（即已访问链接）时用于打印标签的颜色。"""
        return self.GetVisitedColour()

    @单击后焦点颜色.setter
    def 单击后焦点颜色(self, 颜色):
        """设置鼠标悬停在控件上且之前已单击链接（即已访问链接）时用于打印标签的颜色。"""
        self.SetVisitedColour(颜色)

#排序列表框
class wx_adv_EditableListBox(wx.adv.EditableListBox, class_ec):

    @property
    def 项目列表(self):
        """获取排序列表框中的所有项目。"""
        return self.GetStrings()

    @项目列表.setter
    def 项目列表(self, 项目列表):
        """设置排序列表框中的所有项目。"""
        self.SetStrings(项目列表)

#引导按钮
class wx_adv_CommandLinkButton(wx.adv.CommandLinkButton, class_ec):

    @property
    def 主标题(self):
        """获取按钮的主标题。"""
        return self.GetMainLabel()

    @主标题.setter
    def 主标题(self, 标题):
        """设置按钮的主标题。"""
        self.SetMainLabel(标题)

    @property
    def 描述内容(self):
        """获取按钮的描述内容。"""
        return self.GetNote()

    @描述内容.setter
    def 描述内容(self, 描述):
        """设置按钮的描述内容。"""
        self.SetNote(描述)

    def 置标题(self, 标题, 描述):
        """设置按钮的标题和描述，两者之间用第一个换行符分隔，或者不设置空白注释。"""
        self.SetLabel("{}\n{}".format(标题, 描述))

    def 置标题2(self, 标题, 描述):
        """设置按钮的主标题和描述内容。"""
        self.SetMainLabelAndNote(标题, 描述)

#日历框
class wx_adv_CalendarCtrl(wx.adv.CalendarCtrl, class_ec):

    def 突显周末(self, 突显=True):
        """设置是否突显周末。"""
        return self.EnableHolidayDisplay(突显)

    def 允许修改月份(self, 允许=True):
        """设置是否允许修改月份。"""
        return self.EnableMonthChange(允许)

    @property
    def 当前日期(self):
        """获取当前选中的日期。返回格式：2020/9/26 0:00:00"""
        return self.GetDate()

    @当前日期.setter
    def 当前日期(self, 日期):
        """设置当前日期。日期（wx.DateTime）"""
        self.SetDate(日期)

    def 取可选日期范围(self):
        """获取日历控件的可选日期范围。"""
        return self.GetDateRange()

    def 取标题背景色(self):
        """获取日历标题的背景颜色。"""
        return self.GetHeaderColourBg()

    def 取标题前景色(self):
        """获取日历标题的前景颜色。"""
        return self.GetHeaderColourFg()

    def 取背景高光颜色(self):
        """获取日历背景的高光颜色。"""
        return self.GetHighlightColourBg()

    def 取前景高光颜色(self):
        """获取日历前景的高光颜色。"""
        return self.GetHighlightColourFg()

    def 取周末突显背景色(self):
        """获取周末突显的背景颜色。"""
        return self.GetHolidayColourBg()

    def 取周末突显前景色(self):
        """获取周末突显的前景颜色。"""
        return self.GetHolidayColourFg()

    def 标记日期(self, 日期, 标记=True):
        """在日历中标记或取消标记指定日期。日期范围：0-31"""
        self.Mark(日期, 标记)

    def 清除指定日期属性(self, 日期):
        """清除与给定日期相关联的所有属性（范围为1…31）。"""
        self.ResetAttr(日期)

    def 置日期属性(self, 日期, 属性):
        """将属性与指定的日期关联（范围为1…31）"""
        return self.SetAttr(日期, 属性)

    def 置顶部颜色(self, 前景色, 背景色):
        """在控件顶部设置用于平日绘画的颜色。"""
        return self.SetHeaderColours(前景色, 背景色)

    def 置选中日期颜色(self, 前景色, 背景色):
        """设置用于突出显示当前所选日期的颜色。"""
        return self.SetHighlightColours(前景色, 背景色)

    def 某天标记为假日(self, 日期):
        """将指定的日期标记为当前月份的假日。"""
        return self.SetHoliday(日期)

    def 置假日突显颜色(self, 前景色, 背景色):
        """设置用于假日突出显示的颜色。"""
        return self.SetHolidayColours(前景色, 背景色)

#日期框
class wx_adv_DatePickerCtrl(wx.adv.DatePickerCtrl, class_ec):
    @property
    def 可选日期范围(self):
        """获取日期选择控件的可选日期范围。"""
        return self.GetRange()

    @可选日期范围.setter
    def 可选日期范围(self, 范围):
        """设置日期选择控件的可选日期范围。"""
        最早日期, 最晚日期 = 范围
        self.SetRange(最早日期, 最晚日期)

    @property
    def 当前日期(self):
        """获取当前选中的日期。"""
        return self.GetValue()

    @当前日期.setter
    def 当前日期(self, 日期):
        """设置当前日期。"""
        self.SetValue(日期)

#时间框
class wx_adv_TimePickerCtrl(wx.adv.TimePickerCtrl, class_ec):
    @property
    def 当前时间(self):
        """获取当前选中的时间，返回格式为(时, 分, 秒)。"""
        return self.GetTime()

    @当前时间.setter
    def 当前时间(self, 时间):
        """设置当前时间。时间格式为(时, 分, 秒)。"""
        时, 分, 秒 = 时间
        self.SetTime(时, 分, 秒)

    @property
    def 当前时间_dt(self):
        """获取当前时间，返回 wx.DateTime 格式。"""
        return self.GetValue()

    @当前时间_dt.setter
    def 当前时间_dt(self, 时间):
        """设置当前时间，时间为 wx.DateTime 格式。"""
        self.SetValue(时间)

#滚动条
class wx_ScrollBar(wx.ScrollBar, class_ec):
    @property
    def 页面大小(self):
        """获取滚动条的页面大小。"""
        return self.GetPageSize()

    @property
    def 最大位置(self):
        """获取滚动条的最大位置值。"""
        return self.GetRange()

    @property
    def 当前位置(self):
        """获取滚动条当前的位置。"""
        return self.GetThumbPosition()

    @property
    def 滑块大小(self):
        """获取滚动条的滑块大小。"""
        return self.GetThumbSize()

    @property
    def 是否为垂直滚动条(self):
        """判断滚动条是否为垂直方向。"""
        return self.IsVertical()

    @当前位置.setter
    def 当前位置(self, 位置):
        """设置滚动条的当前位置。"""
        self.SetThumbPosition(位置)

    def 置滚动条属性(self, 当前位置, 滑块大小, 最大位置, 页面大小, 是否重绘=True):
        """
        设置滚动条属性。
        :param 当前位置: 滚动条当前的位置。
        :param 滑块大小: 滚动条滑块的大小。
        :param 最大位置: 滚动条的最大位置值。
        :param 页面大小: 滚动条的页面大小。
        :param 是否重绘: 是否重绘滚动条。
        """
        self.SetScrollbar(当前位置, 滑块大小, 最大位置, 页面大小, 是否重绘)

#分组单选框
class wx_RadioBox(wx.RadioBox, class_ec):

    def 启用某项(self, 索引):
        """启用指定索引的选项。"""
        return self.EnableItem(索引, True)

    def 禁用某项(self, 索引):
        """禁用指定索引的选项。"""
        return self.EnableItem(索引, False)

    def 置指定项是否可用(self, 索引, 启用=True):
        """设置指定索引的选项是否可用。"""
        return self.EnableItem(索引, 启用)

    def 查找选项(self, 标题文本, 区分大小写=False):
        """根据标题文本查找选项，返回其索引。"""
        return self.FindString(标题文本, 区分大小写)

    @property
    def 选项列数(self):
        """返回单选框中的列数。"""
        return self.GetColumnCount()

    @property
    def 选项行数(self):
        """返回单选框中的行数。"""
        return self.GetRowCount()

    @property
    def 选项数(self):
        """返回单选框中选项的总数。"""
        return self.GetCount()

    def 取指定坐标处选项(self, x, y):
        """返回指定坐标处的选项索引。"""
        return self.GetItemFromPoint((x, y))

    def 取选项帮助文本(self, 索引):
        """获取指定索引选项的帮助文本。"""
        return self.GetItemHelpText(索引)

    def 取选项文本(self, 索引):
        """获取指定索引选项的文本。"""
        return self.GetItemLabel(索引)

    def 取现行选中项(self):
        """返回当前选中的选项索引。"""
        return self.GetSelection()

    def 是否启用指定项(self, 索引):
        """判断指定索引的选项是否启用。"""
        return self.IsItemEnabled(索引)

    def 是否显示指定项(self, 索引):
        """判断指定索引的选项是否显示。"""
        return self.IsItemShown(索引)

    def 置选项帮助文本(self, 索引, 内容):
        """设置指定索引选项的帮助文本。"""
        return self.SetItemHelpText(索引, 内容)

    def 置选项标题(self, 索引, 标题):
        """设置指定索引选项的标题。"""
        return self.SetItemLabel(索引, 标题)

    def 置选中项(self, 索引):
        """设置指定索引的选项为选中状态。"""
        return self.SetSelection(索引)

    def 显示某项(self, 索引):
        """显示指定索引的选项。"""
        return self.ShowItem(索引, True)

    def 隐藏某项(self, 索引):
        """隐藏指定索引的选项。"""
        return self.ShowItem(索引, False)

    def 显示或隐藏某项(self, 索引, 显示=True):
        """根据指定状态显示或隐藏指定索引的选项。"""
        return self.ShowItem(索引, 显示)

#颜色选择器
class wx_ColourPickerCtrl(wx.ColourPickerCtrl, class_ec):
    @property
    def 当前颜色(self):
        """获取或设置当前选择的颜色。"""
        return self.GetColour()

    @当前颜色.setter
    def 当前颜色(self, 颜色):
        self.SetColour(颜色)

#图文按钮
class lib_button_ThemedGenBitmapTextButton(lib_button.ThemedGenBitmapTextButton, class_ec):
    @property
    def 禁用状态图片(self):
        """获取或设置按钮禁用状态下的图片。"""
        return self.GetBitmapDisabled()

    @禁用状态图片.setter
    def 禁用状态图片(self, 图片):
        self.SetBitmapDisabled(图片)

    @property
    def 焦点状态图片(self):
        """获取或设置按钮焦点状态下的图片。"""
        return self.GetBitmapFocus()

    @焦点状态图片.setter
    def 焦点状态图片(self, 图片):
        self.SetBitmapFocus(图片)

    @property
    def 正常状态图片(self):
        """获取或设置按钮正常状态下的图片。"""
        return self.GetBitmapLabel()

    @正常状态图片.setter
    def 正常状态图片(self, 图片):
        self.SetBitmapLabel(图片)

    @property
    def 按下状态图片(self):
        """获取或设置按钮按下状态下的图片。"""
        return self.GetBitmapSelected()

    @按下状态图片.setter
    def 按下状态图片(self, 图片):
        self.SetBitmapSelected(图片)

#图文按钮L
class lib_gb_GradientButton(lib_gb.GradientButton, class_ec):

    @property
    def 渐变底纹底端颜色(self):
        """获取渐变底纹底端颜色。"""
        return self.GetBottomEndColour()

    @渐变底纹底端颜色.setter
    def 渐变底纹底端颜色(self, 颜色):
        """设置渐变底纹底端颜色。"""
        self.SetBottomEndColour(颜色)

    @property
    def 渐变底纹顶端颜色(self):
        """获取渐变底纹顶端颜色。"""
        return self.GetTopEndColour()

    @渐变底纹顶端颜色.setter
    def 渐变底纹顶端颜色(self, 颜色):
        """设置渐变底纹顶端颜色。"""
        self.SetTopEndColour(颜色)

    @property
    def 渐变底纹底部起始颜色(self):
        """获取渐变底纹底部起始颜色。"""
        return self.GetBottomStartColour()

    @渐变底纹底部起始颜色.setter
    def 渐变底纹底部起始颜色(self, 颜色):
        """设置渐变底纹底部起始颜色。"""
        self.SetBottomStartColour(颜色)

    @property
    def 渐变底纹按下底部起始颜色(self):
        """获取渐变底纹按下底部起始颜色。"""
        return self.GetPressedBottomColour()

    @渐变底纹按下底部起始颜色.setter
    def 渐变底纹按下底部起始颜色(self, 颜色):
        """设置渐变底纹按下底部起始颜色。"""
        self.SetPressedBottomColour(颜色)

    @property
    def 渐变底纹按下顶部起始颜色(self):
        """获取渐变底纹按下顶部起始颜色。"""
        return self.GetPressedTopColour()

    @渐变底纹按下顶部起始颜色.setter
    def 渐变底纹按下顶部起始颜色(self, 颜色):
        """设置渐变底纹按下顶部起始颜色。"""
        self.SetPressedTopColour(颜色)

    @property
    def 渐变底纹顶部起始颜色(self):
        """获取渐变底纹顶部起始颜色。"""
        return self.GetTopStartColour()

    @渐变底纹顶部起始颜色.setter
    def 渐变底纹顶部起始颜色(self, 颜色):
        """设置渐变底纹顶部起始颜色。"""
        self.SetTopStartColour(颜色)

    def 置各状态颜色(self, 起始色, 前景色):
        """设置底部，顶部，按下和前景色。"""
        return self.SetBaseColours(起始色, 前景色)

    def 置图片(self, 图片):
        """设置按钮的图片。"""
        return self.SetBitmapLabel(图片)

    def 置默认按钮(self):
        """将此按钮设置为默认按钮。"""
        return self.SetDefault()

    def 置最佳尺寸(self):
        """将按钮调整为最佳尺寸。"""
        self.SetInitialSize()

#超级链接框L
class lib_hyperlink_HyperLinkCtrl(lib_hyperlink.HyperLinkCtrl, class_ec):

    def 允许打开链接(self, 打开=True):
        """单击后自动浏览到URL。"""
        return self.AutoBrowse(打开)

    def 弹出错误提示(self, 提示内容):
        """弹出错误提示框。"""
        return self.DisplayError(提示内容)

    def 允许右键弹出菜单(self, 弹出=True):
        """允许右键弹出菜单。"""
        return self.DoPopup(弹出)

    def 允许翻转(self, 允许=False):
        """允许翻转，具体功能未知。"""
        return self.EnableRollover(允许)

    @property
    def 标题是否为粗体(self):
        """获取标题是否为粗体。"""
        return self.GetBold()

    @property
    def 默认字体颜色(self):
        """获取默认字体颜色。"""
        return self.GetColours()[0]

    @property
    def 访问后字体颜色(self):
        """获取访问后的字体颜色。"""
        return self.GetColours()[1]

    @property
    def 焦点字体颜色(self):
        """获取焦点字体颜色。"""
        return self.GetColours()[2]

    @property
    def 各种字体颜色(self):
        """获取各种状态下的字体颜色。"""
        return self.GetColours()

    @property
    def 默认标题是否带下划线(self):
        """获取默认标题是否带下划线。"""
        return self.GetUnderlines()[0]

    @property
    def 焦点标题是否带下划线(self):
        """获取焦点状态标题是否带下划线。"""
        return self.GetUnderlines()[1]

    @property
    def 点击后标题是否带下划线(self):
        """获取点击后标题是否带下划线。"""
        return self.GetUnderlines()[2]

    @property
    def 标题是否带各状态下划线(self):
        """获取各状态下标题是否带下划线。"""
        return self.GetUnderlines()

    @property
    def 鼠标光标(self):
        """获取链接的鼠标光标。"""
        return self.GetLinkCursor()

    @property
    def URL(self):
        """获取链接的URL。"""
        return self.GetURL()

    @property
    def 是否已访问过(self):
        """获取链接是否已访问过。"""
        return self.GetVisited()

    def 打开指定链接(self, 链接):
        """打开指定链接。"""
        return self.GotoURL(链接)

    def 置标题字体粗细(self, 粗体=True):
        """设置标题字体粗细。"""
        return self.SetBold(粗体)

    def 置各状态标题颜色(self, 默认, 访问后, 焦点):
        """设置各状态下标题的颜色。"""
        return self.SetColours(默认, 访问后, 焦点)

    def 置默认标题颜色(self, 颜色):
        """设置默认标题颜色。"""
        return self.SetColours(颜色, None, None)

    def 置访问后标题颜色(self, 颜色):
        """设置访问后的标题颜色。"""
        return self.SetColours(None, 颜色, None)

    def 置焦点标题颜色(self, 颜色):
        """设置焦点状态下的标题颜色。"""
        return self.SetColours(None, None, 颜色)

    def 置各状态标题下划线(self, 默认=False, 已访问=False, 焦点=False):
        """设置各状态下标题是否带下划线。"""
        return self.SetUnderlines(默认, 已访问, 焦点)

    def 置默认标题下划线(self, 下划线=True):
        """设置默认状态下标题是否带下划线。"""
        return self.SetUnderlines(下划线, None, None)

    def 置访问后标题下划线(self, 下划线=True):
        """设置访问后标题是否带下划线。"""
        return self.SetUnderlines(None, 下划线, None)

    def 置焦点标题下划线(self, 下划线=True):
        """设置焦点状态下标题是否带下划线。"""
        return self.SetUnderlines(None, None, 下划线)

    def 置URL(self, url):
        """设置链接的URL。"""
        return self.SetURL(url)

    def 置访问状态(self, 状态=True):
        """设置链接是否已被访问。"""
        return self.SetVisited(状态)

    def 更新链接(self, 刷新控件=True):
        """更新链接，可选择是否刷新控件。"""
        self.UpdateLink(刷新控件)

#小数微调框
class lib_fs_FloatSpin(lib_fs.FloatSpin, class_ec):

    @property
    def 当前数值(self):
        """获取当前设置的数值。"""
        return self.GetValue()

    @当前数值.setter
    def 当前数值(self, 数值):
        """设置当前数值。"""
        self.SetValue(数值)

    @property
    def 默认数值(self):
        """获取默认的数值。"""
        return self.GetDefaultValue()

    @property
    def 显示的位数(self):
        """获取显示的小数位数。"""
        return self.GetDigits()

    @显示的位数.setter
    def 显示的位数(self, 位数):
        """设置显示的小数位数。"""
        self.SetDigits(位数)

    @property
    def 字符格式(self):
        """获取字符格式。"""
        return self.GetFormat()

    @字符格式.setter
    def 字符格式(self, 格式):
        """设置字符格式。"""
        self.SetFormat(格式)

    @property
    def 最大值(self):
        """获取允许的最大值。"""
        return self.GetMax()

    @最大值.setter
    def 最大值(self, 最大值):
        """设置允许的最大值。"""
        self.SetMax(最大值)

    @property
    def 最小值(self):
        """获取允许的最小值。"""
        return self.GetMin()

    @最小值.setter
    def 最小值(self, 最小值):
        """设置允许的最小值。"""
        self.SetMin(最小值)

    def 置数值范围(self, 最小值, 最大值):
        """设置允许的数值范围。"""
        self.SetRange(最小值, 最大值)

    def 置数值范围2(self, 最小值, 最大值):
        """设置允许的数值范围，不限制当前值。"""
        self.SetRangeDontClampValue(最小值, 最大值)

    def 是否设置数值范围(self):
        """检查是否已设置数值范围。"""
        return self.HasRange()

    def 是否在数值范围内(self, 数值):
        """检查指定数值是否在允许的范围内。"""
        return self.InRange(数值)

    def 是否已设置默认值(self):
        """检查是否已设置默认值。"""
        return self.IsDefaultValue()

#超级列表框
class wx_ListCtrl(wx.ListCtrl, class_ec):

    def 加入行(self, 内容列表):
        """在末尾加入新一行数据，返回加入的行索引"""
        return self.Append(内容列表)

    def 加入列(self, 标题, 对齐方式=2, 宽度=-1):
        """
        在末尾加入新一列
        :param 标题: 自己定
        :param 对齐方式: 0.左对齐  1.右对齐 2.居中
        :param 宽度: 自己定
        :return: 加入的列索引
        """
        return self.AppendColumn(标题, 对齐方式, 宽度)

    def 排列项目(self, 排列方式=0):
        """
        在图标或小图标视图中排列项目
        :param 排列方式: 0.默认对齐方式  1.与控件的左侧对齐 2.与控件的顶部对齐 3.对齐网格
        :return:
        """
        return self.Arrange(排列方式)

    def 置选中状态(self, 索引, 选中=True):
        """使用复选框选中或取消选中控件中的wx.ListItem"""
        return self.CheckItem(索引, 选中)

    def 全部删除(self):
        """删除所有项目和所有列"""
        return self.ClearAll()

    def 删除所有列(self):
        return self.DeleteAllColumns()

    def 删除所有行(self):
        return self.DeleteAllItems()

    def 删除指定列(self, 列索引):
        return self.DeleteColumn(列索引)

    def 删除指定行(self, 行索引):
        return self.DeleteItem(行索引)

    def 开始编辑(self, 行索引):
        """需要设置了 wx.LC_EDIT_LABELS 样式才能使用,开始编辑指定行的第一列"""
        return self.EditLabel(行索引)

    def 启用或禁用交替行背景色(self, 启用=True):
        """
        启用交替的行背景色（也称为斑马条纹）,
        该方法只能在虚拟报表模式（即具有LC_REPORT 和LC_VIRTUAL 样式）中为控件调用。
        """
        return self.EnableAlternateRowColours(启用)

    def 启用或禁用按键搜索(self, 启用):
        """只匹配第一列，从键盘搜索项目时，如果当前输入的文本不匹配，则启用或禁用蜂鸣声。"""
        return self.EnableBellOnNoMatch(启用)

    def 启用或禁用选择框(self, 启用=True):
        """启用或禁用列表项的复选框"""
        return self.EnableCheckBoxes(启用)

    def 启用或禁用系统主题样式(self, 启用=True):
        return self.EnableSystemTheme(启用)

    def 保证显示(self, 行索引):
        return self.EnsureVisible(行索引)

    def 保证显示2(self, 行索引):
        return self.Focus(行索引)

    def 查找表项(self, 查找的内容, 开始索引=-1, 模糊查找=False):
        """只查找第一列"""
        return self.FindItem(开始索引, 查找的内容, 模糊查找)

    def 取交替行背景色(self):
        return self.GetAlternateRowColour()

    def 取列对象(self, 列索引):
        return self.GetColumn(列索引)

    def 取列标题(self, 列索引):
        return self.GetColumn(列索引).GetText()

    def 取列对齐方式(self, 列索引):
        """对齐方式：0.左对齐 1.右对齐 2.居中"""
        return self.GetColumn(列索引).GetAlign()

    def 取列宽(self, 列索引):
        return self.GetColumnWidth(列索引)

    def 取列数(self):
        return self.GetColumnCount()

    def 取可视列索引(self, 索引):
        """一般用不上，除非你调整了列排序啥的我也没用过"""
        return self.GetColumnOrder(索引)

    def 取列顺序索引(self):
        """一般用不上除非你改动了列，返回一个列表，包含列索引数值"""
        return self.GetColumnsOrder()

    def 取可见行数(self):
        """返回列表框完全可见的行数"""
        return self.GetCountPerPage()

    def 取编辑控件对象(self):
        """返回当前用于编辑标签的编辑控件。None如果没有标签被编辑，则返回"""
        return self.GetEditControl()

    def 取现行选中项(self):
        """返回第一个选定的项目；如果未选择任何项目，则返回-1。"""
        return self.GetFirstSelected()

    def 取现行焦点项(self):
        """获取当前焦点的项目；如果没有焦点，则返回-1。"""
        return self.GetFocusedItem()

    def 取图片组列表(self, 类型):
        """图片组类型：0.普通(大图列表)  1.小图列表  2.自定义列表  返回类型wx.ImageList"""
        return self.GetImageList(类型)

    def 取行数(self):
        return self.GetItemCount()

    def 取行对象(self, 行索引):
        return self.GetItem(行索引)

    def 取行背景色(self, 行索引):
        return self.GetItemBackgroundColour(行索引)

    def 取行字体(self, 行索引):
        return self.GetItemFont(行索引)

    def 取行坐标(self, 行索引):
        """返回指定行所在的x,y坐标"""
        return self.GetItemPosition(行索引)

    def 取行矩形(self, 行索引):
        """返回指定行的矩形"""
        return self.GetItemRect(行索引)

    def 取图标间距(self):
        return self.GetItemSpacing()

    def 取行状态(self, 行索引, 类型=wx.LIST_STATE_SELECTED):
        """默认返回是否为现行选中项"""
        return bool(self.GetItemState(行索引, 类型))

    def 取标题(self, 行索引, 列索引):
        return self.GetItemText(行索引, 列索引)

    def 取行文本颜色(self, 行索引):
        """
        如果项目没有特定的颜色，则返回无效的颜色（而不是控件本身的默认前景色控件，
        因为这不允许区分与当前控件前景色相同颜色的项目和默认颜色的项目，
        因此，与控件始终具有相同的颜色）。
        """
        return self.GetItemTextColour(行索引)

    def 取下一选中项(self, 当前索引):
        """返回指定行下面的现行选中项，没有就返回-1"""
        return self.GetNextSelected(当前索引)

    def 取选中表项数(self):
        return self.GetSelectedItemCount()

    def 取文本颜色(self):
        return self.GetTextColour()

    def 取首个可见索引(self):
        """在列表或报表视图中获取最顶部可见项目的索引"""
        return self.GetTopItem()

    def 取最大尺寸(self):
        """
        请注意，此功能仅在图标，小图标或报告查看模式中有效，而在列表视图或报表视图中则无效（这是本机Win32控件的限制）。
        返回控件中所有项目采用的矩形。
        换句话说，如果控件客户端的大小等于此矩形的大小，则不需要滚动条，也不会留下可用空间。
        """
        return self.GetViewRect()

    def 是否启用选择框(self):
        return self.HasCheckBoxes()

    def 是否带LC_REPORT样式(self):
        """单列或多列报表视图，带有可选标题。"""
        return self.InReportView()

    def 插入列(self, 插入位置, 标题, 对齐方式=2, 宽度=-1):
        """
        在末尾加入新一列
        :param 标题: 自己定
        :param 对齐方式: 0.左对齐  1.右对齐 2.居中
        :param 宽度: 自己定
        :return: 加入的列索引
        """
        return self.InsertColumn(插入位置, 标题, 对齐方式, 宽度)

    def 插入行(self, 插入位置, 标题):
        """只能插入第一个标题"""
        return self.InsertItem(插入位置, 标题)

    def 插入图片(self, 插入位置, 图片索引):
        """与此控件和视图样式关联的图像列表的索引"""
        return self.InsertItem(插入位置, 图片索引)

    def 插入图文(self, 插入位置, 标题, 图片索引):
        """插入图像/字符串项目。"""
        return self.InsertItem(插入位置, 标题, 图片索引)

    def 是否无表项(self):
        """具有某些列的控件如果没有行，则仍被认为是空的。"""
        return self.IsEmpty()

    def 是否选中(self, 行索引):
        """判断该行选择框是否勾选"""
        return self.IsItemChecked(行索引)

    def 是否为选择项(self, 索引):
        """返回True是否选择了该项目，不是选中"""
        return self.IsSelected(索引)

    def 是否为虚拟报表(self):
        """返回True该控件当前是否在虚拟报表视图中。"""
        return self.IsVirtual()

    def 表项是否可见(self, 行索引):
        """检查项目是否可见。"""
        return self.IsVisible(行索引)

    def 取指定行图片索引(self, 行索引):
        """它应返回控件图像列表中项目图像的索引，如果没有图像，则返回-1"""
        return self.OnGetItemImage(行索引)

    def 是否选中2(self, 行索引):
        """它应该返回是否选中了指定 item 复选框。对于具有 使用复选框的样式的控件，必须在派生类中重写 此函数LC_VIRTUAL。"""
        return self.OnGetItemIsChecked(行索引)

    def 取标题2(self, 行索引, 列索引):
        """它应返回包含 指定 的给定列文本的字符串item。对于具有 样式的控件，必须在派生类中重写 此函数LC_VIRTUAL。"""
        return self.OnGetItemText(行索引, 列索引)

    def 重画指定项目(self, 行索引):
        return self.RefreshItem(行索引)

    def 重画指定范围项目(self, 起始行, 结束行):
        """正如RefreshItem，这仅对虚拟列表控件有用。起始项必须小于或等于结束项。重绘itemFrom 和itemTo之间的项目。"""
        return self.RefreshItems(起始行, 结束行)

    def 滚动滚动条(self, dx, dy):
        """如果处于图标，小图标或报告查看模式，则dx 指定要滚动的像素数。如果处于列表视图模式，则dx 指定要滚动的列数。dy 始终指定要垂直滚动的像素数。"""
        return self.ScrollList(dx, dy)

    def 选择某项(self, 行索引):
        """选择不是选中"""
        return self.Select(行索引)

    def 置备用行背景色(self, 颜色):
        """将备用行背景色设置为特定颜色。与一样EnableAlternateRowColours，此方法只能与具有LC_REPORT 和LC_VIRTUAL 样式的控件一起使用"""
        return self.SetAlternateRowColour(颜色)

    def 置列标题(self, 列索引, 标题):
        Item = self.GetColumn(列索引)
        Item.SetText(标题)
        return self.SetColumn(列索引, Item)

    def 置列宽(self, 列索引, 宽度):
        return self.SetColumnWidth(列索引, 宽度)

    def 置列对齐方式(self, 列索引, 对齐方式):
        """对齐方式: 0.左对齐  1.右对齐 2.居中"""
        Item = self.GetColumn(列索引)
        Item.SetAlign(对齐方式)
        return self.SetColumn(列索引, Item)

    def 置列图片(self, 列索引, 图片):
        return self.SetColumnImage(列索引, 图片)

    def 置列排序位置(self, 排序列表):
        """修改列的位置"""
        return self.SetColumnsOrder(排序列表)

    def 置列标题字体颜色(self, attr):
        """更改用于列表控件标题的字体和颜色。"""
        return self.SetHeaderAttr(attr)

    def 置关联图片列表(self, 图片列表):
        return self.SetImageList(图片列表)

    def 置标题(self, 行索引, 列索引, 标题):
        return self.SetItem(行索引, 列索引, 标题)

    def 置图文(self, 行索引, 列索引, 标题, 图片索引):
        return self.SetItem(行索引, 列索引, 标题, 图片索引)

    def 置行色(self, 行索引, 颜色):
        return self.SetItemBackgroundColour(行索引, 颜色)

    def 置图片(self, 行索引, 列索引, 图片索引):
        return self.SetItemColumnImage(行索引, 列索引, 图片索引)

    def 置行数(self, 行数):
        """此方法只能与虚拟列表控件一起使用。没用过"""
        return self.SetItemCount(行数)

    def 置行字体(self, 行索引, 字体):
        return self.SetItemFont(行索引, 字体)

    def 置选中状态图片(self, 行索引, 选中图索引, 未选中图索引):
        """设置与项目关联的未选择和选择的图像。"""
        return self.SetItemImage(行索引, 选中图索引, 未选中图索引)

    def 置项目坐标(self, 项目索引, x, y):
        """在图标或小图标视图中设置项目的位置。"""
        return self.SetItemPosition(项目索引, (x, y))

    def 置选择状态(self, 行索引, 是否选择):
        状态 = 4 if 是否选择 else 0
        return self.SetItemState(行索引, 状态, wx.LIST_STATE_SELECTED)

    def 置标题_首列(self, 行索引, 标题):
        return self.SetItemText(行索引, 标题)

    def 置行文本颜色(self, 行索引, 颜色):
        return self.SetItemTextColour(行索引, 颜色)

    def 添加列表样式(self, 样式):
        return self.SetSingleStyle(样式, True)

    def 删除列表样式(self, 样式):
        return self.SetSingleStyle(样式, False)

    def 置全部文本颜色(self, 颜色):
        return self.SetTextColour(颜色)

    def 置窗口新样式(self, 样式):
        return self.SetWindowStyleFlag(样式)

    def 显示或隐藏列(self, 列索引, 显示=True):
        """显示或隐藏指定的列"""
        return self.ShowColumn(列索引, 显示)

    def 切换列顺序(self, 列索引):
        """切换指定列的顺序"""
        return self.SwitchColumnOrder(列索引)

    def 切换列顺序2(self, 旧列索引, 新列索引):
        """将一列从一个位置移动到另一个位置"""
        return self.SwapColumns(旧列索引, 新列索引)

    def 取列可见状态(self, 列索引):
        """返回指定列是否可见"""
        return self.IsColumnShown(列索引)

    def 取首个未选中项(self):
        """获取首个未选中的项索引，如果没有则返回 -1"""
        return self.GetFirstUnselected()

    def 取插入标记位置(self):
        """获取当前插入标记的位置"""
        return self.GetInsertionPoint()

    def 设置插入标记(self, 行索引, 在前面=True):
        """设置插入标记的位置。如果在前面为 True，则在该行之前插入，否则在该行之后插入"""
        return self.SetInsertionPoint(行索引, 在前面)

    def 启用或禁用拖放排序(self, 启用=True):
        """启用或禁用用户通过拖放重新排序列的功能"""
        return self.EnableColumnDrag(启用)

    def 启用或禁用列头排序(self, 启用=True):
        """启用或禁用用户点击列头进行排序的功能"""
        return self.EnableColumnOrder(启用)

    def 列排序指示器(self, 列索引, 方向):
        """
        在指定的列标题上显示排序指示器。
        :param 方向: 0.不显示 1.向上（升序） 2.向下（降序）
        """
        return self.ShowSortIndicator(列索引, 方向)

    def 取列排序指示器方向(self, 列索引):
        """获取指定列标题上的排序指示器方向"""
        return self.GetSortIndicator(列索引)


# 选择夹
class wx_Notebook(class_ec,wx.Notebook):

    @property
    def 现行子夹(self):
        return self.GetSelection()

    @现行子夹.setter
    def 现行子夹(self, 序号):
        return self.SetSelection(序号)

    def 删除所有子夹(self):
        self.DeleteAllPages()

    def 删除子夹(self,序号):
        self.DeletePage(序号)

    def 取现行子夹对象(self):
        return self.GetCurrentPage()

    def 取子夹数量(self):
        return self.GetPageCount()

    def 添加子夹(self,窗口,标题,是否选中=False):
        self.AddPage(page=窗口,text=标题,select=是否选中)

# 面板
class wx_Panel(class_ec,wx.Panel):
    pass

# 属性框
class wx_propgrid_PropertyGrid(class_ec,wx.propgrid.PropertyGrid):
    pass






