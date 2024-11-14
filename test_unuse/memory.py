import psutil
import time

def monitor_system_and_process_resources(pid, interval=1):
    process = psutil.Process(pid)
    try:
        # 获取初始CPU时间，用于计算CPU使用率
        initial_cpu_times = process.cpu_times()
        while True:
            # 获取内存信息
            memory_info = process.memory_info()
            memory_usage_mb = memory_info.rss / (1024 * 1024)
            
            # 获取CPU信息
            current_cpu_times = process.cpu_times()
            total_time = sum(current_cpu_times) - sum(initial_cpu_times)
            cpu_usage_percent = process.cpu_percent(interval=None)
            
            # 获取系统级别的IO信息
            disk_io = psutil.disk_io_counters()
            net_io = psutil.net_io_counters()
            
            # 打印信息
            print(f"系统资源使用情况：")
            print(f"  磁盘读取速度：{disk_io.read_bytes / interval / (1024 * 1024):.2f} MB/s")
            print(f"  磁盘写入速度：{disk_io.write_bytes / interval / (1024 * 1024):.2f} MB/s")
            print(f"  网络发送速度：{net_io.bytes_sent / interval / (1024 * 1024):.2f} MB/s")
            print(f"  网络接收速度：{net_io.bytes_recv / interval / (1024 * 1024):.2f} MB/s")
            
            print(f"进程 {pid} 的资源使用情况：")
            print(f"  内存使用量：{memory_usage_mb:.2f} MB")
            print(f"  CPU使用率：{cpu_usage_percent:.2f}%")
            
            # 更新CPU时间，用于下一次计算
            initial_cpu_times = current_cpu_times
            
            # 等待下一个时间间隔
            time.sleep(interval)
    except psutil.NoSuchProcess:
        print(f"进程 {pid} 不存在。")
    except psutil.AccessDenied:
        print(f"没有权限访问进程 {pid} 的信息。")
    except KeyboardInterrupt:
        print("监控被用户中断。")

# 使用示例
pid_to_monitor = 1 # 假设 cls.pid 是你想要监控的进程ID
monitor_system_and_process_resources(pid_to_monitor)
