import yaml
from functools import reduce
import operator
import copy

class Config:
    config:dict = None

    @classmethod
    def string_to_number(cls, s):
        # 将字符串按 * 分割成数字字符串列表，并转换为整数列表
        numbers = map(int, s.split('*'))
        # 使用 reduce 和 operator.mul 计算乘积
        return reduce(operator.mul, numbers)

    @classmethod
    def reload_config(cls,conf_path="config.yaml"):
        with open(conf_path, mode='r', encoding='utf-8') as f:
            cls.config = yaml.safe_load(f)
    
    @classmethod
    def get_reader_config(cls) -> dict:
        cls.get_config()
        reader_config = copy.deepcopy(cls.config.get("reader"))
        block_size = reader_config.get("block_size", 1024*4)
        if isinstance(block_size, str):
            reader_config["block_size"] = cls.string_to_number(block_size)
        big_block_size = reader_config.get("big_block_size", 1024*4)
        if isinstance(big_block_size, str):
            reader_config["big_block_size"] = cls.string_to_number(big_block_size)
        return reader_config
    
    @classmethod
    def get_log_config(cls):
        cls.get_config()
        log_config = copy.deepcopy(cls.config.get("log"))
        return log_config
    
    @classmethod
    def get_config(cls):
        if cls.config == None:
            cls.reload_config()
        return cls.config


if __name__=="__main__":
    config = Config.get_config()
    print(config)