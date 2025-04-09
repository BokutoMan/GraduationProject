# app/auth/routes.py
from functools import partial
import hashlib
import os
import time
import uuid
from flask import Blueprint, jsonify, request
from API.setup import init_global as G

dfh_bp = Blueprint('dfh', __name__, url_prefix='/dfh')  # 统一前缀 /auth

@dfh_bp.route('/process', methods=['POST'])
def start_process():
    task_id = str(uuid.uuid4())  # 唯一任务标识
    file_path = request.json['file_path']
    
    # 非阻塞尝试获取信号量（并发控制核心）
    # 如果 G.semaphore._value > 0 则立即获取，否则不阻塞
    print(G.semaphore.get_value())
    if G.semaphore.acquire(block=False):  
        # 记录任务初始状态（共享字典自动同步）
        G.task_status[task_id] = {'status': 'processing'}
        
        # ======== 提交任务到进程池 =======
        G.task_pool.apply_async(
            process_file_task,    # 目标处理函数
            args=(file_path, task_id, G.progress_queue),  # 传递task_id到子进程
            callback=partial(_task_success, task_id),  # 成功回调
            error_callback=partial(_task_failed, task_id)  # 异常回调
        )
        return jsonify({'task_id': task_id})
    else:
        # 返回HTTP 503服务不可用（流量控制）
        return jsonify({'error': 'Server busy'}), 503  
    
@dfh_bp.route('/status/<task_id>')
def get_status(task_id):
    status = G.task_status.get(task_id, {'error': 'Invalid task ID'})
    return jsonify({
        'status': status.get('status'),
        'progress': status.get('progress', 0),  # 新增进度字段
        'result': status.get('result')
    })

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
    
def _task_success(task_id, result):
    """任务成功回调（在主进程执行）"""
    G.semaphore.release()  # 释放信号量
    G.task_status[task_id] = {  # 更新共享状态
        'status': 'completed',
        'result': result
    }

def _task_failed(task_id, exc):
    """任务异常回调（在主进程执行）"""
    G.semaphore.release()  # 必须释放信号量
    G.task_status[task_id] = {
        'status': 'error',
        'result': str(exc)
    }