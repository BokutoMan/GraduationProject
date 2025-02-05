from utils import Config, SimpleLogger
import os
import yaml

class ToolManager:
    def __init__(self, config_path="global_config.yaml"):
        self.configs = self.load(config_path)

    def load(self, path=None):
        with open( path,  "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def reload(self, path=None):
        self.global_config = self.load(path)

    def get_config(self, name):
        config = self.configs.get(name)
        if config is None:
            raise Exception(f"Config {name} not found")
        re = Config(conf_path=config.get("config_path"), name=name)
        return re
    
    def get_logger(self, name):
        config = self.configs.get(name)
        if config is None:
            raise Exception("Config {name} not found")
        logger = SimpleLogger.get_new_logger(name=name, log_file=config.get("log_path"))
        return logger
