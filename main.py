import time
from pathlib import Path
from core.file_watcher import FileMonitor
from config.config_loader import load_config  # 导入封装的工具方法

if __name__ == "__main__":
    config = load_config()  # 调用封装的方法
    
    # 创建输入输出目录
    Path(config['paths']['input_folder']).mkdir(exist_ok=True)
    Path(config['paths']['output_folder']).mkdir(exist_ok=True)
    
    # 启动文件监控
    monitor = FileMonitor(config['paths']['input_folder'])
    monitor.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.observer.stop()
    monitor.observer.join()