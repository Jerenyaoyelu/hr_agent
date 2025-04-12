import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ResumeWatcher(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        
    def on_created(self, event):
        if not event.is_directory:
            self.callback(Path(event.src_path))

class FileMonitor:
    def __init__(self, watch_path):
        self.observer = Observer()
        self.watch_path = Path(watch_path)
        self.handler = ResumeWatcher(self.process_file)
        
    def start(self):
        self.observer.schedule(self.handler, str(self.watch_path))
        self.observer.start()
        print(f"开始监控文件夹: {self.watch_path}")
        
    def process_file(self, file_path):
        if file_path.suffix.lower() not in ['.pdf', '.docx', '.doc']:
            print(f"忽略非简历文件: {file_path.name}")
            return

        if file_path.name.startswith('~$'):
            print(f"忽略临时文件: {file_path.name}")
            return

        print(f"发现新简历: {file_path.name}")
        # 触发处理流水线
        from core.pipeline import process_resume
        import asyncio

        # 检查是否在事件循环中
        try:
            loop = asyncio.get_running_loop()
            # 如果有事件循环，创建任务
            loop.create_task(process_resume(file_path))
        except RuntimeError:
            # 如果没有事件循环，直接运行
            asyncio.run(process_resume(file_path))