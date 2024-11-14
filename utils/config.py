import yaml
from functools import reduce
import operator

class Config:
    config:dict = None

    @classmethod
    def string_to_number(cls, s):
        # 将字符串按 * 分割成数字字符串列表，并转换为浮点数列表
        numbers = map(int, s.split('*'))
        # 使用 reduce 和 operator.mul 计算乘积
        return reduce(operator.mul, numbers)

    @classmethod
    def reload_config(cls,conf_path="config.yaml"):
        with open(conf_path, mode='r', encoding='utf-8') as f:
            cls.config = yaml.safe_load(f)
         # 将字符串按 * 分割成数字字符串列表，并转换为浮点数列表
        block_size = cls.config.get("block_size", "1024*")
        if isinstance(block_size, str):
            cls.config["block_size"] = cls.string_to_number(block_size)
    
    @classmethod
    def get_config(cls):
        if cls.config == None:
            cls.reload_config()
        return cls.config


if __name__=="__main__":
    config = Config.get_config()
    print(config)