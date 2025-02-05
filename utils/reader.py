import os
from utils import Config
from logging import Logger
from comm import hash_mm3_64


class Reader:
    def __init__(self, config:dict=None, logger:Logger=None,
                 file_paths=None, block_size=None, 
                 big_block_size=None, sampling_range=None, 
                 random_pre=None, pre=None, 
                 is_batch_reading=None, batch_size=None,
                 small_file_size=None):
        """
        从多个文件中随机采样满足哈希条件的块。如果不传入参数，则使用配置文件中的默认值。
        
        :param config: Config().read_config() 返回的配置字典。
        :param logger: 日志记录器。
        :param file_paths: 文件或文件夹路径列表。
        :param block_size: 每个块的大小（以字节为单位）。
        :param big_block_size: 大块的大小（以字节为单位）。
        :param sampling_range: 元组形式的哈希采样范围 (lower, higher)，在 [0, 1] 范围内。
        :param random_pre: 随机预处理的标志。
        :param pre: hash的标志。
        :param is_batch_reading: 是否启用批量读取。
        :param batch_size: 批量读取时每次读取的比例。
        :param small_file_size: 读取的最小文件的大小。
        """
        # 获取配置或使用默认值
        get_value = lambda a, b: a if a is not None else b
        self.file_paths = get_value(file_paths, config.get("read_file_paths"))
        self.block_size = get_value(block_size, config.get("block_size"))
        self.big_block_size = get_value(big_block_size, config.get("big_block_size"))
        self.lower, self.higher = get_value(sampling_range, (config.get("range").get("lower"), config.get("range").get("higher")))
        self.random_pre = get_value(random_pre, config.get("random_pre"))
        if self.random_pre:
            charset = "qbcdefghijklmnopqrstuvwxyz"
            import random
            self.prefix = ''.join(random.choice(charset) for _ in range(5))
        else:
            self.prefix = get_value(pre, config.get("prefix"))
        self.is_batch_reading = get_value(is_batch_reading, config.get("is_batch_reading"))
        self.batch_size = get_value(batch_size, config.get("batch_size"))
        self.logger = logger  # 初始化 logger

        # 参数验证
        if self.block_size <= 0 or self.big_block_size <= 0:
            raise ValueError("Block size and big block size must be positive integers.")
        if not (0 <= self.lower < self.higher <= 1):
            raise ValueError("Sampling range must be within [0, 1] and lower <= higher.")
        if self.is_batch_reading and not (0 <= self.batch_size <= 1) :
            raise ValueError("Batch size must be within [0, 1] when batch reading is enabled.")
        
        # 获取所有需要读取的文件
        self.small_file_size = get_value(small_file_size, config.get("small_file_size"))
        self.read_file_paths, self.total_size = self.get_files(self.file_paths, self.small_file_size)

        if self.is_batch_reading:
            self.now_lower = self.lower
            self.now_higher = self.batch_size
        else:
            self.now_lower = self.lower
            self.now_higher = self.higher

    # 重置配置
    def set_new_reader(self, **kargs):
        self.__init__(**kargs)
        
    @staticmethod
    def get_files(file_paths, size):
        # size转换为字节
        size_in_bytes = size
        result = []
        total_size = 0
        
        for path in file_paths:
            if os.path.isdir(path):  # 如果是目录
                for root, dirs, files in os.walk(path):  # 遍历目录及其子目录
                    for file in files:
                        file_path = os.path.join(root, file)
                        # 获取文件大小
                        if os.path.getsize(file_path) > size_in_bytes:
                            total_size += os.path.getsize(file_path)
                            result.append(file_path)
            elif os.path.isfile(path):  # 如果是文件
                if os.path.getsize(path) > size_in_bytes:
                    total_size += os.path.getsize(path)
                    result.append(path)
        return result, total_size

    def _read_blocks(self):
        """
        遍历文件列表，按哈希值采样块，返回块。
        """
        for file_path in self.read_file_paths:
            if not os.path.isfile(file_path):
                self.logger.warning(f"File not found: {file_path}")  # 使用 logger 记录警告
                continue

            file_size = os.path.getsize(file_path)
            num_blocks = (file_size + self.big_block_size - 1) // self.big_block_size  # 计算总块数

            self.logger.info(
                f"Reading from: {file_path} - "
                f"File size: {file_size / 1024 / 1024 / 1024 :.2f} GB - "
                f"Blocks to read: {int(num_blocks*(self.higher-self.lower))} big blocks, "
                f"{int(num_blocks*(self.higher-self.lower)) * self.big_block_size // self.block_size} small blocks"
            )  # 使用 logger 记录信息

            with open(file_path, 'rb') as file:
                for block_index in range(num_blocks):
                    # 计算当前块的起始位置
                    start_pos = block_index * self.big_block_size
                    identifier = f"{file_path}:{start_pos}:{self.prefix}"

                    # 使用哈希值决定是否采样
                    hash_value = hash_mm3_64(identifier)
                    if self.lower <= hash_value <= self.higher:
                        file.seek(start_pos)
                        block_data = file.read(self.big_block_size)

                        # 分割大块为小块
                        for i in range(0, len(block_data), self.block_size):
                            yield block_data[i:i + self.block_size]

    def _read_blocks_batch(self):
        """
        每个batch返回一个生成器
        """
        while self.now_lower <= self.higher:
            yield self._read_blocks()
            self.now_lower = self.now_lower + self.batch_size
            self.now_higher = self.now_higher + self.batch_size
            if self.now_higher > self.higher:
                self.now_higher = self.higher

    def get_reader(self):
        """
        获取或重新创建 Reader。
        """
        if not self.is_batch_reading:
            return self._read_blocks()
        else:
            return self._read_blocks_batch()


if __name__=="__main__":
    from utils import ToolManager
    tm = ToolManager()

    reader = Reader(config=tm.get_config(name="test1").get_reader_config(),
                    logger=tm.get_logger(name="test1"))
    
    read = reader.get_reader()
    print(read)
    i = 0
    for data in read:
        i += 1
    print(i)