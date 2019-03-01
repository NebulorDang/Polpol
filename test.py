#encoding=utf-8
# 创建队列实例， 用于存储任务
import queue
import time
import threading
from threading import Thread
queue = queue.Queue()

# 定义需要线程池执行的任务
def do_job():
    while True:
        i = queue.get()
        time.sleep(1)
        print ('index %s, curent: %s' % (i, threading.current_thread()))
        queue.task_done()

if __name__ == '__main__':
    # 创建包括3个线程的线程池
    for i in range(3):
        t = Thread(target=do_job)
        t.daemon=True # 设置线程daemon  主线程退出，daemon线程也会推出，即时正在运行
        t.start()

    # 模拟创建线程池3秒后塞进10个任务到队列
    time.sleep(3)
    for i in range(10):
        queue.put(i)

    queue.join()