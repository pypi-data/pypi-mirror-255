# -*- coding: utf-8 -*-
import queue,random

class 队列:

    def __init__(self, 队列大小: int = 0, 顺序: bool = True):
        """
        初始化队列。

        :param 队列大小: 队列的最大大小，小于1表示无限长。
        :param 顺序: 为真则队列是先进先出，为假则队列是后进先出。
        """
        if 顺序:
            self.__队列 = queue.Queue(maxsize=队列大小)
        else:
            self.__队列 = queue.LifoQueue(maxsize=队列大小)

    def 是否为空(self) -> bool:
        """
        检查队列是否为空。

        :return: 为空返回True，否则返回False。
        """
        return self.__队列.empty()

    def 是否已满(self) -> bool:
        """
        检查队列是否已满。

        :return: 已满返回True，否则返回False。
        """
        return self.__队列.full()

    def 清空队列(self):
        """
        清空队列中的所有元素。
        """
        while not self.__队列.empty():
            self.__队列.get()

    def 取出成员(self):
        """
        从队列中取出一个元素。

        :return: 取出的元素，如果队列为空，则返回None。
        """
        if not self.__队列.empty():
            return self.__队列.get()
        else:
            return None

    def 取队列成员数(self) -> int:
        """
        获取队列中的元素数量。

        :return: 队列中的元素数量。
        """
        return self.__队列.qsize()

    def 加入成员(self, 值):
        """
        向队列中加入一个元素。

        :param 值: 加入队列的元素。
        """
        self.__队列.put(值)

class 字典类(dict):
    def __init__(self, 初始字典=None):
        """
        初始化字典类的实例。

        :param 初始字典: 用于初始化的字典。
        """
        super().__init__(初始字典 or {})

    def 取值并删除(self, 键, 失败返回值=None):
        """
        如果键存在于字典中，则删除并返回其值；如果不存在，则返回失败返回值。
        :param 键: 要删除的键。
        :param 失败返回值: 如果键不存在时的返回值。
        :return: 删除的键对应的值或失败返回值。
        示例：字典实例.取值并删除('a') # 返回 1
        """
        return self.pop(键, 失败返回值)

    def 取指定键值(self, 键, 失败返回值=None):
        """
        如果键存在于字典中，则返回其值；如果不存在，则返回失败返回值。
        :param 键: 要查找的键。
        :param 失败返回值: 如果键不存在时的返回值。
        :return: 键对应的值或失败返回值。
        示例：字典实例.取指定键值('a') # 返回 1
        """
        return self.get(键, 失败返回值)

    def 清空(self):
        """
        清空字典中的所有项。
        :return: 总是返回True。
        示例：字典实例.清空() # 返回 True
        """
        self.clear()
        return True

    def 拷贝(self):
        """
        创建字典的浅拷贝。
        :return: 字典的一个新的浅拷贝。
        示例：副本 = 字典实例.拷贝() # 创建一个新的字典副本
        """
        return 字典类(self.copy())

    @staticmethod
    def 生成(键值列表, 键值):
        """
        从键列表创建一个新字典，所有键对应的值都是相同的。
        :param 键值列表: 字典键的列表。
        :param 键值: 所有键的共同值。
        :return: 一个新的字典。
        示例：新字典 = 字典类.生成(['a', 'b', 'c'], 1) # 返回 {'a': 1, 'b': 1, 'c': 1}
        """
        return 字典类.fromkeys(键值列表, 键值)

    def 转列表(self):
        """
        将字典的键值对转换为列表。
        :return: 包含字典键值对的列表。
        示例：字典实例.转列表() # 返回 [('a', 1), ('b', 2), ('c', 3)]
        """
        return list(self.items())

    def 取全部键(self):
        """
        返回字典中所有键的列表。
        :return: 字典键的列表。
        示例：字典实例.取全部键() # 返回 ['a', 'b', 'c']
        """
        return list(self.keys())

    def 取全部值(self):
        """
        返回字典中所有值的列表。
        :return: 字典值的列表。
        示例：字典实例.取全部值() # 返回 [1, 2, 3]
        """
        return list(self.values())

    def 取出并删除最后键值(self):
        """
        删除并返回字典中的最后一个键值对。
        :return: 被删除的键值对。
        示例：字典实例.取出并删除最后键值() # 返回 ('c', 3)
        """
        return self.popitem()

    def 取值添加(self, 键, 值=None):
        """
        如果键不存在于字典中，将键值添加到字典。
        :param 键: 要添加的键。
        :param 值: 要添加的值。
        :return: 键对应的值。
        示例：字典实例.取值添加('d', 4) # 返回 4
        """
        return self.setdefault(键, 值)

class 列表类(list):
    def __init__(self, 初始列表=None):
        """
        初始化列表类的实例。

        :param 初始列表: 用于初始化的列表。
        """
        super().__init__(初始列表 or [])

    def 转字典(self):
        """
        将列表转换为字典。
        列表格式应为[(1,2),(3,4)]。
        """
        return {x[0]: x[1] for x in self}

    @staticmethod
    def 合并为字典(列表1, 列表2):
        """
        将两个列表合并为字典。
        例如：[1,2]和[8,9]合并为{1:8, 2:9}。
        """
        return dict(zip(列表1, 列表2))

    def 加入成员(self, 值):
        """
        在列表末尾添加新的对象。
        """
        self.append(值)
        return True

    def 插入成员(self, 位置, 值):
        """
        在指定位置插入一个项目。
        """
        self.insert(位置, 值)
        return True

    def 取出现次数(self, 值):
        """
        返回元素在列表中出现的次数。
        """
        return self.count(值)

    def 合并列表(self, 新列表):
        """
        合并另一个列表或元组到当前列表。
        """
        self.extend(新列表)
        return True

    def 查找成员位置(self, 值):
        """
        返回列表中值的第一个匹配项的索引。
        """
        return self.index(值)

    def 取值并删除(self, 位置=None):
        """
        移除列表中的一个元素（默认最后一个元素），并且返回该元素的值。
        """
        return self.pop(位置) if 位置 is not None else self.pop()

    def 删除指定值(self, 值):
        """
        移除列表中值为 x 的第一个元素。
        """
        self.remove(值)
        return True

    def 倒序排列(self):
        """
        将列表中的元素反向排列。
        """
        self.reverse()
        return True

    def 大小排序(self, 排序方式=False):
        """
        对列表进行排序。
        """
        self.sort(reverse=排序方式)
        return True

def 数组_按成员长度排序(数组):
    """
    根据数组中每个成员的长度进行排序，长度长的在前。

    :param 数组: 要排序的数组。
    :return: 排序后的新数组。
    示例：数组_按成员长度排序(['apple', 'pear', 'banana']) # 返回 ['banana', 'apple', 'pear']
    """
    return sorted(数组, key=lambda i: len(i), reverse=True)


def 数组_按子成员大小排序(数组, 成员索引):
    """
    根据数组中子成员的大小进行排序。

    :param 数组: 包含子数组的数组。
    :param 成员索引: 子数组中用于排序的成员索引。
    :return: 排序后的新数组。
    示例：数组_按子成员大小排序([[1, 'apple'], [3, 'banana'], [2, 'pear']], 0) # 返回 [[3, 'banana'], [2, 'pear'], [1, 'apple']]
    """
    return sorted(数组, key=lambda i: i[成员索引])


def 数组_取随机成员数组(数组, 数量):
    """
    从数组中随机取出指定数量的成员组成新数组。

    :param 数组: 原数组。
    :param 数量: 要取出的成员数量。
    :return: 新数组，包含随机选取的成员。
    示例：数组_取随机成员数组([1, 2, 3, 4, 5], 3) # 可能返回 [3, 1, 5]
    """
    return random.sample(数组, 数量) if 数量 <= len(数组) else False


def 数组_取随机成员(数组):
    """
    从数组中随机取出一个成员。

    :param 数组: 原数组。
    :return: 随机选取的一个成员。
    示例：数组_取随机成员([1, 2, 3, 4, 5]) # 可能返回 3
    """
    return random.choice(数组)