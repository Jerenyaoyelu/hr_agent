 import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import csv
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import pandas as pd

class ResultPersistence:
    def __init__(self, output_dir: str, smtp_config: Optional[Dict[str, str]] = None):
        """
        初始化结果持久化模块
        
        Args:
            output_dir: 输出目录
            smtp_config: SMTP服务器配置（可选）
                {
                    'host': SMTP服务器地址,
                    'port': 端口,
                    'username': 用户名,
                    'password': 密码,
                    'from_email': 发件人邮箱
                }
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.smtp_config = smtp_config
        
    def save_resume_analysis(self, candidate_id: str, 
                           analysis_result: Dict[str, Any]):
        """保存简历分析结果"""
        try:
            # 创建候选人目录
            candidate_dir = self.output_dir / candidate_id
            candidate_dir.mkdir(exist_ok=True)
            
            # 保存JSON格式的分析结果
            analysis_file = candidate_dir / 'resume_analysis.json'
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"已保存简历分析结果：{analysis_file}")
            
        except Exception as e:
            self.logger.error(f"保存简历分析结果失败: {str(e)}")
            raise
            
    def save_evaluation_result(self, candidate_id: str, 
                             evaluation_result: Dict[str, Any]):
        """保存评估结果"""
        try:
            candidate_dir = self.output_dir / candidate_id
            candidate_dir.mkdir(exist_ok=True)
            
            # 保存JSON格式的评估结果
            evaluation_file = candidate_dir / 'evaluation_result.json'
            with open(evaluation_file, 'w', encoding='utf-8') as f:
                json.dump(evaluation_result, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"已保存评估结果：{evaluation_file}")
            
        except Exception as e:
            self.logger.error(f"保存评估结果失败: {str(e)}")
            raise
            
    def save_interview_schedule(self, candidate_id: str, 
                              schedule_info: Dict[str, Any]):
        """保存面试安排"""
        try:
            candidate_dir = self.output_dir / candidate_id
            candidate_dir.mkdir(exist_ok=True)
            
            # 保存JSON格式的面试安排
            schedule_file = candidate_dir / 'interview_schedule.json'
            with open(schedule_file, 'w', encoding='utf-8') as f:
                json.dump(schedule_info, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"已保存面试安排：{schedule_file}")
            
        except Exception as e:
            self.logger.error(f"保存面试安排失败: {str(e)}")
            raise
            
    def generate_summary_report(self, start_date: datetime, 
                              end_date: datetime) -> str:
        """生成汇总报告"""
        try:
            # 收集指定日期范围内的所有数据
            data = []
            for candidate_dir in self.output_dir.iterdir():
                if not candidate_dir.is_dir():
                    continue
                    
                # 读取简历分析结果
                analysis_file = candidate_dir / 'resume_analysis.json'
                if analysis_file.exists():
                    with open(analysis_file, 'r', encoding='utf-8') as f:
                        analysis = json.load(f)
                        
                    # 读取评估结果
                    evaluation_file = candidate_dir / 'evaluation_result.json'
                    evaluation = None
                    if evaluation_file.exists():
                        with open(evaluation_file, 'r', encoding='utf-8') as f:
                            evaluation = json.load(f)
                            
                    # 读取面试安排
                    schedule_file = candidate_dir / 'interview_schedule.json'
                    schedule = None
                    if schedule_file.exists():
                        with open(schedule_file, 'r', encoding='utf-8') as f:
                            schedule = json.load(f)
                            
                    # 整合数据
                    record = {
                        'candidate_id': candidate_dir.name,
                        'name': analysis.get('name'),
                        'evaluation_score': evaluation.get('score') if evaluation else None,
                        'recommendation': evaluation.get('recommendation') if evaluation else None,
                        'interview_status': schedule.get('status') if schedule else None
                    }
                    data.append(record)
                    
            # 生成Excel报告
            df = pd.DataFrame(data)
            report_file = self.output_dir / f'summary_report_{start_date.strftime("%Y%m%d")}-{end_date.strftime("%Y%m%d")}.xlsx'
            df.to_excel(report_file, index=False)
            
            self.logger.info(f"已生成汇总报告：{report_file}")
            return str(report_file)
            
        except Exception as e:
            self.logger.error(f"生成汇总报告失败: {str(e)}")
            raise
            
    def send_email_notification(self, to_email: str, subject: str, 
                              content: str, attachments: Optional[List[str]] = None):
        """发送邮件通知"""
        if not self.smtp_config:
            self.logger.warning("未配置SMTP服务器，无法发送邮件")
            return
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['from_email']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # 添加正文
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            # 添加附件
            if attachments:
                for file_path in attachments:
                    with open(file_path, 'rb') as f:
                        part = MIMEApplication(f.read())
                        part.add_header('Content-Disposition', 'attachment', 
                                      filename=Path(file_path).name)
                        msg.attach(part)
                        
            # 发送邮件
            with smtplib.SMTP(self.smtp_config['host'], 
                            int(self.smtp_config['port'])) as server:
                server.starttls()
                server.login(self.smtp_config['username'], 
                           self.smtp_config['password'])
                server.send_message(msg)
                
            self.logger.info(f"已发送邮件至：{to_email}")
            
        except Exception as e:
            self.logger.error(f"发送邮件失败: {str(e)}")
            raise