import os
import threading

def exec_in_available_thread(func, *args, **kwargs):
    if os.cpu_count() > threading.active_count():
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
    else:
        func(*args, **kwargs)