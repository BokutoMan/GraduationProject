import multiprocessing
from multiprocessing.managers import SyncManager
import multiprocessing.synchronize
import multiprocessing.pool

from queue import Empty

# 使用Manager实现跨进程共享数据
# 使用Pool创建进程池，BoundedSemaphore控制并发量
from multiprocessing import Pool, BoundedSemaphore, Manager, cpu_count
from threading import Thread

progress_queue : SyncManager.Queue = None
queue_consumer : Thread = None
task_pool : multiprocessing.pool.Pool = None
task_status : SyncManager.dict = None
MAX_WORKERS : int = None
semaphore :multiprocessing.synchronize.BoundedSemaphore  = None

# ======== 全局资源初始化 ========
def init_globals():
    global progress_queue, queue_consumer, task_pool, task_status, MAX_WORKERS, semaphore
    
    # 最大工作进程数 = CPU核心数-3（避免过度分配）
    MAX_WORKERS = cpu_count()  - 3
    
    # 信号量控制（关键并发控制组件）
    # BoundedSemaphore可防止意外多次release导致计数溢出
    semaphore = BoundedSemaphore(MAX_WORKERS)
    
    # Manager创建的共享字典（跨进程安全）
    # 用于跟踪所有任务状态
    manager = Manager()
    task_status = manager.dict()
    
    # 进程池初始化（核心工作引擎）
    task_pool = Pool(
        processes=MAX_WORKERS,  # 与信号量大小一致
        initializer=app_init,   # 子进程初始化函数
        maxtasksperchild=100    # 每个子进程处理100次任务后重启（避免内存泄漏）
    )

    # 创建进度队列和锁
    progress_queue = Manager().Queue()
    # 启动队列消费线程
    queue_consumer = Thread(target=update_progress_from_queue, daemon=True)
    queue_consumer.start()

def app_init():
    """子进程初始化（每个工作进程启动时执行）"""
    import signal
    # 忽略子进程的键盘中断信号（由主进程统一处理）
    signal.signal(signal.SIGINT, signal.SIG_IGN)  
    # 可在此添加数据库连接池等资源初始化

def update_progress_from_queue():
    """后台线程：持续从队列读取进度并更新共享字典"""
    while True:
        try:
            task_id, progress = progress_queue.get(timeout=1)
            if task_id in task_status:
                task_status[task_id]['progress'] = progress
        except Empty:
            from API.setup.init_app import app
            if app is not None and app.config.get('EXITING'):
                break