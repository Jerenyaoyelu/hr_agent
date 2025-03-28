import yaml
from pathlib import Path
from core.file_watcher import FileMonitor

def load_config():
    with open("config/settings.yaml") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    config = load_config()
    
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