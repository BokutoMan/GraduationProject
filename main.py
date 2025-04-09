from API.setup import init_global as G
from flask import Flask
app = None


import signal

def register_shutdown_hook():
    """注册应用退出钩子"""
    def _shutdown(signum, frame):
        # 设置退出标志
        app.config['EXITING'] = True
        G.task_pool.close()  # 停止接受新任务
        G.task_pool.join()   # 等待所有工作进程结束
        app.stop()
        exit(0)
    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

if __name__ == '__main__':
    app = Flask(__name__)
    G.init_globals()
    from API.app.routes.calculator_dfh import dfh_bp
    app.register_blueprint(dfh_bp)
    register_shutdown_hook()
    app.run(threaded=True, port=5000)