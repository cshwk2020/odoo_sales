import queue
import threading

progress_queue = queue.Queue()
stop_flag = threading.Event()
