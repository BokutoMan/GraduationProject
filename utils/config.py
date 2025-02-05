import yaml
from functools import reduce
import operator
import copy

class Config:
    def __init__(self, conf_path="config/config.yaml", name=None):
        self.config:dict = None
        self.conf_path = conf_path
        self.name = name
        self.reload_config(conf_path=conf_path)


    @staticmethod
    def string_to_number(s):
        # 将字符串按 * 分割成数字字符串列表，并转换为整数列表
        numbers = map(int, s.split('*'))
        # 使用 reduce 和 operator.mul 计算乘积
        return reduce(operator.mul, numbers)

    def reload_config(self, conf_path="config.yaml"):
        self.conf_path = conf_path
        with open(conf_path, mode='r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
    
    def get_reader_config(self) -> dict:
        self.get_config()
        reader_config = copy.deepcopy(self.config.get("reader"))
        block_size = reader_config.get("block_size", 1024*4)
        if isinstance(block_size, str):
            reader_config["block_size"] = self.string_to_number(block_size)
        big_block_size = reader_config.get("big_block_size", 1024*4)
        if isinstance(big_block_size, str):
            reader_config["big_block_size"] = self.string_to_number(big_block_size)
        small_file_size = reader_config.get("small_file_size", 4)
        if isinstance(small_file_size, str):
            reader_config["small_file_size"] = self.string_to_number(small_file_size)
        return reader_config
    
    def get_log_config(self):
        self.get_config()
        log_config = copy.deepcopy(self.config.get("log"))
        return log_config
    
    def get_config(self):
        if self.config == None:
            self.reload_config()
        return self.config


if __name__=="__main__":
    config = Config().get_config()
    print(config)