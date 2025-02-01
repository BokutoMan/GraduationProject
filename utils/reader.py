import os
from utils.config import Config
from comm import hash_mm3_64


class Reader:
    reader = None

    @classmethod
    def set_new_reader(cls, file_paths=None, block_size=None, big_block_size=None, sampling_range=None):
        """
        从多个文件中随机采样满足哈希条件的块。
        
        :param file_paths: 文件路径列表。
        :param block_size: 每个块的大小（以字节为单位）。
        :param big_block_size: 大块的大小（以字节为单位）。
        :param sampling_range: 元组形式的哈希采样范围 (lower, higher)，在 [0, 1] 范围内。
        """
        # 获取配置或使用默认值
        config = Config.get_reader_config()
        file_paths = file_paths or config.get("read_file_paths")
        block_size = block_size or config.get("block_size")
        big_block_size = big_block_size or config.get("big_block_size")
        lower, higher = sampling_range or (config.get("range").get("lower"), config.get("range").get("hight"))

        # 参数验证
        if block_size <= 0 or big_block_size <= 0:
            raise ValueError("Block size and big block size must be positive integers.")
        if not (0 <= lower < higher <= 1):
            raise ValueError("Sampling range must be within [0, 1] and lower <= higher.")

        # 生成器返回分块数据
        return cls._read_blocks(file_paths, block_size, big_block_size, lower, higher)

    @staticmethod
    def get_files(file_paths, size):
        # size转换为字节
        size_in_bytes = size * 1024
        result = []
        
        for path in file_paths:
            if os.path.isdir(path):  # 如果是目录
                for root, dirs, files in os.walk(path):  # 遍历目录及其子目录
                    for file in files:
                        file_path = os.path.join(root, file)
                        # 获取文件大小
                        if os.path.getsize(file_path) > size_in_bytes:
                            result.append(file_path)
            elif os.path.isfile(path):  # 如果是文件
                if os.path.getsize(path) > size_in_bytes:
                    result.append(path)
        
        return result

    @classmethod
    def _read_blocks(cls, file_paths, block_size, big_block_size, lower, higher):
        """
        遍历文件列表，按哈希值采样块，返回文件名与偏移地址。
        """
        file_paths =  cls.get_files(file_paths, 100)
        for file_path in file_paths:
            if not os.path.isfile(file_path):
                print(f"Warning: File not found: {file_path}")
                continue

            file_size = os.path.getsize(file_path)
            num_blocks = (file_size + big_block_size - 1) // big_block_size  # 计算总块数

            print(
                f"\nReading from: {file_path}\n"
                f"File size: {file_size / 1024 / 1024 / 1024 :.2f} GB\n"
                f"Blocks to read: {int(num_blocks*(higher-lower))} big blocks, "
                f"{int(num_blocks*(higher-lower)) * big_block_size // block_size} small blocks"
            )

            with open(file_path, 'rb') as file:
                for block_index in range(num_blocks):
                    # 计算当前块的起始位置
                    start_pos = block_index * big_block_size
                    identifier = f"{file_path}:{start_pos}"

                    # 使用哈希值决定是否采样
                    hash_value = hash_mm3_64(identifier)
                    if lower <= hash_value <= higher:
                        file.seek(start_pos)
                        block_data = file.read(big_block_size)

                        # 分割大块为小块
                        for i in range(0, len(block_data), block_size):
                            yield block_data[i:i + block_size]

    @classmethod
    def get_reader(cls, new=False):
        """
        获取或重新创建 Reader。
        """
        if cls.reader is None or new:
            cls.reader = cls.set_new_reader()
        return cls.reader


if __name__=="__main__":
    # i = 0
    # import time
    # start_time = time.time()
    # reader = Reader.get_reader()
    # # from utils.log import SimpleLogger
    # for block_data in reader:
    #     print(f'\r {i}, {len(block_data)}', end="")
    #     i += 1
    #     # SimpleLogger.memory_log()
    # end_time = time.time()
    # print()
    # print(f"运行时间为: {end_time - start_time:.3f} 秒")
    files = [r"D:\temp\ubuntu.iso" , r"D:\Software\VM_VirtualMachine"]
    files_ = Reader.get_files(files, 100)
    print(len(files_))