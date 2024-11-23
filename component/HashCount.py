from dataclasses import dataclass

@dataclass
class HashCount:
    hash: float
    count: int

    # 重载 == 运算符，hash 值相等表示对象相等
    def __eq__(self, other):
        if isinstance(other, HashCount):
            return self.hash == other.hash
        return False

    # 重载 < 运算符，基于 hash 值进行比较
    def __lt__(self, other):
        if isinstance(other, HashCount):
            return self.hash < other.hash
        return NotImplemented

    # 重载 <= 运算符，基于 hash 值进行比较
    def __le__(self, other):
        if isinstance(other, HashCount):
            return self.hash <= other.hash
        return NotImplemented

    # 重载 > 运算符，基于 hash 值进行比较
    def __gt__(self, other):
        if isinstance(other, HashCount):
            return self.hash > other.hash
        return NotImplemented

    # 重载 >= 运算符，基于 hash 值进行比较
    def __ge__(self, other):
        if isinstance(other, HashCount):
            return self.hash >= other.hash
        return NotImplemented

    # 重载 + 运算符，当与正整数n相加时，count += n；当与HashCount类型对象相加时，只有hash值相等时，count相加
    def __add__(self, other):
        if isinstance(other, int) and other > 0:
            # 如果与正整数相加，count += n
            return HashCount(self.hash, self.count + other)
        elif isinstance(other, HashCount) and self.hash == other.hash:
            # 如果与HashCount对象相加，并且hash值相等，count相加
            return HashCount(self.hash, self.count + other.count)
        return NotImplemented

    # 重载 += 运算符，当与正整数n相加时，count += n；当与HashCount类型对象相加时，只有hash值相等时，count相加
    def __iadd__(self, other):
        if isinstance(other, int) and other > 0:
            # 如果与正整数相加，count += n
            self.count += other
            return self
        elif isinstance(other, HashCount) and self.hash == other.hash:
            # 如果与HashCount对象相加，并且hash值相等，count相加
            self.count += other.count
            return self
        return NotImplemented

if __name__=="__main__":
    # 示例使用
    obj1 = HashCount(hash=1.23, count=10)
    obj2 = HashCount(hash=1.23, count=15)
    obj3 = HashCount(hash=2.34, count=5)

    # + 运算符
    result1 = obj1 + 5  # 与正整数相加
    result2 = obj1 + obj2  # 与 HashCount 对象相加，hash 相等
    result3 = obj1 + obj3  # 与 hash 不同的 HashCount 对象相加

    print(result1)  # HashCount(hash=1.23, count=15)
    print(result2)  # HashCount(hash=1.23, count=25)
    print(result3)  # HashCount(hash=1.23, count=10) (无变化)

    # += 运算符
    obj1 += 10  # 与正整数相加
    obj2 += obj3  # 与 hash 不同的 HashCount 对象相加
    obj1 += obj2  # 与 hash 相同的 HashCount 对象相加

    print(obj1)  # HashCount(hash=1.23, count=20)
    print(obj2)  # HashCount(hash=1.23, count=15) (无变化)
