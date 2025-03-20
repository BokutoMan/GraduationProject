import os
from queue import Empty
import time
from flask import Flask, jsonify, request
# 使用Manager实现跨进程共享数据
# 使用Pool创建进程池，BoundedSemaphore控制并发量
from multiprocessing import Pool, BoundedSemaphore, Manager, cpu_count
import hashlib
from threading import Thread
import uuid
from functools import partial

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
            if app.config.get('EXITING'):
                break

# ========= Flask路由控制 ==========
@app.route('/process', methods=['POST'])
def start_process():
    task_id = str(uuid.uuid4())  # 唯一任务标识
    file_path = request.json['file_path']
    
    # 非阻塞尝试获取信号量（并发控制核心）
    # 如果 semaphore._value > 0 则立即获取，否则不阻塞
    print(semaphore.get_value())
    if semaphore.acquire(block=False):  
        # 记录任务初始状态（共享字典自动同步）
        task_status[task_id] = {'status': 'processing'}
        
        # ======== 提交任务到进程池 =======
        task_pool.apply_async(
            process_file_task,    # 目标处理函数
            args=(file_path, task_id, progress_queue),  # 传递task_id到子进程
            callback=partial(_task_success, task_id),  # 成功回调
            error_callback=partial(_task_failed, task_id)  # 异常回调
        )
        return jsonify({'task_id': task_id})
    else:
        # 返回HTTP 503服务不可用（流量控制）
        return jsonify({'error': 'Server busy'}), 503  

def _task_success(task_id, result):
    """任务成功回调（在主进程执行）"""
    semaphore.release()  # 释放信号量
    task_status[task_id] = {  # 更新共享状态
        'status': 'completed',
        'result': result
    }

def _task_failed(task_id, exc):
    """任务异常回调（在主进程执行）"""
    semaphore.release()  # 必须释放信号量
    task_status[task_id] = {
        'status': 'error',
        'result': str(exc)
    }

# ======= 工作进程任务 ========
def process_file_task(file_path, task_id, progress_queue):
    print(f"Processing task_id: {task_id}")
    """子进程任务函数（新增进度上报）"""
    try:
        print("task ", task_id, "started")
        file_size = os.path.getsize(file_path)
        processed_bytes = 0
        update_interval = 1  # 每秒更新一次进度
        hashes = {}  # 注意：此字典是子进程局部变量
        duplicate_count = 0
        
        with open(file_path, 'rb') as f:
            last_update = time.time()
            while chunk := f.read(4096):
                # 处理数据块...
                h = hashlib.sha256(chunk).hexdigest()
                if h in hashes:
                    duplicate_count += 1
                else:
                    hashes[h] = 1
                processed_bytes += len(chunk)
                
                # 按时间间隔上报进度
                if time.time() - last_update > update_interval:
                    progress = min(100, (processed_bytes / file_size) * 100)
                    progress_queue.put((task_id, progress))
                    last_update = time.time()
                    print(progress)
        
        # 最终进度强制设为100%
        progress_queue.put((task_id, 100))
        return {'duplicates': duplicate_count}
    except Exception as e:
        progress_queue.put((task_id, -1))  # 错误标识
        raise RuntimeError(f"Process failed: {str(e)}")

# ========= 状态查询接口 ==========
@app.route('/status/<task_id>')
def get_status(task_id):
    print("task_status", task_status)
    status = task_status.get(task_id, {'error': 'Invalid task ID'})
    return jsonify({
        'status': status.get('status'),
        'progress': status.get('progress', 0),  # 新增进度字段
        'result': status.get('result')
    })

import signal

def register_shutdown_hook():
    """注册应用退出钩子"""
    def _shutdown(signum, frame):
        app.config['EXITING'] = True
        task_pool.close()  # 停止接受新任务
        task_pool.join()   # 等待所有工作进程结束
        app.stop()
        exit(0)
    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

if __name__ == '__main__':
    init_globals()
    app = Flask(__name__)
    register_shutdown_hook()
    app.run(threaded=True, port=5000)