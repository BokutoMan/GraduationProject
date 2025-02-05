import string

class SaveDFH:
    """
    将浮点数映射到唯一字符串的类
    """
    def __init__(self, name:str):
        # 选择字符集，这里选择a-zA-Z（52个字符）来组合一个3字符的字符串
        self.char_set = string.ascii_lowercase + string.ascii_uppercase  # 'a-zA-Z' -> 52个字符
        self.num_chars = len(self.char_set)
        self.name = name

    def save_dfh(self, dfh:list, p:float, msg=""):
        import json
        import time
        var = self.float_to_str(p)
        with open(f"data/dfh/{self.name}.py", "+a", encoding="utf-8") as f:
            f.write(f'# {time.strftime(r"%Y-%m-%d %H:%M:%S")} , p = {p} {msg}\n' + f"{var} = {json.dumps(dfh)}\n")

    def get_dfh(self, p:float):
        """
        # 根据概率 p 获取对应的 dfh
        """
        var = self.float_to_str(p)
        import importlib
        # 动态导入模块
        model_name = f"data.dfh.{self.name}"
        module = importlib.import_module(model_name)
        dfh = getattr(module, var, None)
        if dfh is None:
            raise ValueError(f"{self.name} 概率 {p} dfh 变量 {var} 不存在")
        re = []
        for i in dfh:
            if isinstance(i, list):
                re.append(tuple(i))
            else:
                re.append(i)
        return re

    # 函数1：浮点数转字符串（精确到三位小数）
    def float_to_str(self, f):
        """
        将0到1之间的浮点数（精确到三位小数）映射到一个唯一的字符串
        """
        if not (0 <= f <= 1):
            raise ValueError("浮点数必须在0到1之间")
        
        # 将浮点数转换为三位小数
        f = round(f, 3)
        
        # 将浮动值映射到 0 到 999
        index = int(f * 1000)
        
        # 使用字符集来生成一个3个字符的字符串
        first_char = self.char_set[index // (self.num_chars**2)]  # 高位
        second_char = self.char_set[(index // self.num_chars) % self.num_chars]  # 中位
        third_char = self.char_set[index % self.num_chars]  # 低位
        
        return first_char + second_char + third_char

    # 函数2：字符串转浮点数
    def str_to_float(self, s):
        """
        将字符组成的字符串映射回浮点数（精确到三位小数）
        """
        if len(s) != 3 or any(c not in self.char_set for c in s):
            raise ValueError("输入的字符串必须是3个字符，并且每个字符必须在预定义字符集内")
        
        # 计算字符的索引
        index = (self.char_set.index(s[0]) * self.num_chars**2 +
                self.char_set.index(s[1]) * self.num_chars +
                self.char_set.index(s[2]))
        
        # 将索引映射回浮动值
        return round(index / 1000, 3)

if __name__ == "__main__":
    # 测试
    float_to_str = SaveDFH(name="test")
    for i in range(1000):
        f = 0.001 + i * 0.001
        s = float_to_str.float_to_str(f)

        str_val = s
        fl = float_to_str.str_to_float(str_val)
        if round(fl, 3) != round(f, 3):
            print(f"字符串 {str_val} 映射回浮动值: {fl} 失败", f"f = {f}")
    else:
        print("测试通过！")

    sd = SaveDFH(name="test")
    sd.save_dfh([1, 2, 3, 5, 2, 3, (4,5), {"sds": 555}], 0.991, msg="测试")
    data = sd.get_dfh(0.991)
    print(data)
