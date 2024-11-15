import os
import random
from utils.config import Config

class Reader:
    reader = None
    config = Config.get_reader_config()

    @classmethod
    def set_new_reader(cls, file_path=config.get("read_file_path"), 
                       block_size=config.get("block_size"), percentage=config.get("percentage"), 
                       big_block_size=config.get("big_block_size")):
        """
        从大文件中随机读取一定比例的块。

        :param file_path: 文件路径。
        :param block_size: 每个块的大小（以字节为单位），默认为1MB。
        :param percentage: 要读取的块的比例（例如，15表示15%）。
        """
        file_size = os.path.getsize(file_path)
        num_blocks = (file_size + big_block_size - 1) // big_block_size  # 计算总块数
        num_blocks_to_read = int(num_blocks * (percentage / 100))  # 计算要读取的块数
        print(file_path, "大小为", file_size//1024//1024//1024, "GB", \
              f"共读取{num_blocks_to_read}个大块,{num_blocks_to_read*big_block_size//block_size}个小块")

        # 随机选择要读取的块索引
        blocks_to_read = random.sample(range(num_blocks), num_blocks_to_read)

        with open(file_path, 'rb') as file:
            for block_index in blocks_to_read:
                # 计算当前块的起始位置
                start_pos = block_index * big_block_size
                file.seek(start_pos)

                # 读取当前块的数据
                block_data = file.read(big_block_size)
                
                # 分割 big_block_size 块为多个 block_size 小块，并依次返回
                for i in range(0, len(block_data), block_size):
                    yield block_data[i:i+block_size]

    @classmethod
    def get_reader(cls, new=False):
        if cls.reader == None or new:
            cls.reader = cls.set_new_reader()
        return cls.reader

if __name__=="__main__":
    i = 0
    import time
    start_time = time.time()
    reader = Reader.get_reader()
    from utils.log import SimpleLogger
    for block_data in reader:
        print(f'\r {i}, {len(block_data)}', end="")
        i += 1
        SimpleLogger.memory_log()
    end_time = time.time()
    print()
    print(f"运行时间为: {end_time - start_time:.8f} 秒")