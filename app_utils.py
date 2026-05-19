from .globals import progress_queue

def debugText(text):
    print("server side:", text)
    progress_queue.put(text)

def mask_password(pwd: str) -> str:
    return "*" * len(pwd)
