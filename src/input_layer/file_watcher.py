
import os
import time
from pathlib import Path
from typing import Callable, List, Optional
import logging

class FileWatcher:
    def __init__(self, watch_dir: str, supported_extensions: List[str] = ['.pdf', '.doc', '.docx']):
        """
        初始化文件监听器
        
        Args:
            watch_dir: 要监控的文件夹路径
            supported_extensions: 支持的简历文件扩展名列表
        """
        self.watch_dir = Path(watch_dir)
        self.supported_extensions = supported_extensions
        self.processed_files = set()
        self.logger = logging.getLogger(__name__)
        
    def start_watching(self, callback: Callable[[Path], None], interval: float = 1.0):
        """
        开始监控文件夹
        
        Args:
            callback: 当发现新文件时调用的回调函数
            interval: 检查间隔（秒）
        """
        self.logger.info(f"开始监控文件夹: {self.watch_dir}")
        
        while True:
            try:
                # 获取当前文件夹中的所有文件
                current_files = set()
                for ext in self.supported_extensions:
                    current_files.update(self.watch_dir.glob(f"*{ext}"))
                
                # 找出新文件
                new_files = current_files - self.processed_files
                
                # 处理新文件
                for file_path in new_files:
                    self.logger.info(f"发现新文件: {file_path}")
                    try:
                        callback(file_path)
                        self.processed_files.add(file_path)
                    except Exception as e:
                        self.logger.error(f"处理文件 {file_path} 时出错: {str(e)}")
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"监控过程中出错: {str(e)}")
                time.sleep(interval)
    
    def get_unprocessed_files(self) -> List[Path]:
        """
        获取所有未处理的文件
        
        Returns:
            未处理文件的路径列表
        """
        current_files = set()
        for ext in self.supported_extensions:
            current_files.update(self.watch_dir.glob(f"*{ext}"))
        return list(current_files - self.processed_files)