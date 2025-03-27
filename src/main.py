import os
import logging
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

from input_layer.file_watcher import FileWatcher
from core_pipeline.resume_parser import ResumeParser
from core_pipeline.resume_evaluator import ResumeEvaluator, JobRequirement
from core_pipeline.interview_scheduler import InterviewScheduler, Candidate, Interviewer
from output_layer.persistence import ResultPersistence

class HRAgent:
    def __init__(self, config_path: str):
        """
        初始化HR Agent
        
        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
            
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config['log_file']),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # 初始化各个模块
        self.file_watcher = FileWatcher(
            self.config['watch_dir'],
            self.config.get('supported_extensions', ['.pdf', '.doc', '.docx'])
        )
        
        self.resume_parser = ResumeParser(self.config['openai_api_key'])
        
        self.resume_evaluator = ResumeEvaluator(self.config['openai_api_key'])
        
        self.interview_scheduler = InterviewScheduler(self.config['openai_api_key'])
        
        self.persistence = ResultPersistence(
            self.config['output_dir'],
            self.config.get('smtp_config')
        )
        
        # 加载职位要求
        self.job_requirement = JobRequirement(**self.config['job_requirement'])
        
        # 加载面试官信息
        self.interviewers = [
            Interviewer(**interviewer_data)
            for interviewer_data in self.config['interviewers']
        ]
        
    def process_resume(self, file_path: Path):
        """处理单个简历文件"""
        try:
            # 生成候选人ID
            candidate_id = datetime.now().strftime("%Y%m%d%H%M%S")
            
            # 解析简历
            self.logger.info(f"开始解析简历：{file_path}")
            resume_data = self.resume_parser.parse_resume(file_path)
            
            # 保存解析结果
            self.persistence.save_resume_analysis(
                candidate_id,
                resume_data.to_dict()
            )
            
            # 评估简历
            self.logger.info("开始评估简历")
            evaluation_result = self.resume_evaluator.evaluate_resume(
                resume_data,
                self.job_requirement
            )
            
            # 保存评估结果
            self.persistence.save_evaluation_result(
                candidate_id,
                {
                    'score': evaluation_result.score,
                    'matching_skills': evaluation_result.matching_skills,
                    'missing_skills': evaluation_result.missing_skills,
                    'experience_match': evaluation_result.experience_match,
                    'education_match': evaluation_result.education_match,
                    'detailed_feedback': evaluation_result.detailed_feedback,
                    'recommendation': evaluation_result.recommendation
                }
            )
            
            # 如果评分达到面试标准，安排面试
            if evaluation_result.score >= 60:
                self.logger.info("安排面试")
                candidate = Candidate(
                    name=resume_data.name,
                    email=resume_data.email,
                    phone=resume_data.phone or ""
                )
                
                interview = self.interview_scheduler.schedule_interview(
                    candidate,
                    self.interviewers
                )
                
                if interview:
                    # 保存面试安排
                    self.persistence.save_interview_schedule(
                        candidate_id,
                        {
                            'start_time': interview.start_time.isoformat(),
                            'end_time': interview.end_time.isoformat(),
                            'location': interview.location,
                            'status': interview.status,
                            'interviewers': [
                                {'name': i.name, 'email': i.email}
                                for i in interview.interviewers
                            ]
                        }
                    )
                    
                    # 发送邮件通知
                    if self.config.get('smtp_config'):
                        self.persistence.send_email_notification(
                            candidate.email,
                            "面试邀请",
                            f"""
                            尊敬的 {candidate.name}：
                            
                            我们很高兴地通知您，您已通过初步简历筛选，我们诚挚地邀请您参加面试。
                            
                            面试时间：{interview.start_time.strftime('%Y-%m-%d %H:%M')} - {interview.end_time.strftime('%H:%M')}
                            面试地点：{interview.location}
                            
                            请提前10分钟进入会议室/到达面试地点。
                            如有任何问题，请随时与我们联系。
                            
                            祝好！
                            """
                        )
            
            self.logger.info(f"简历处理完成：{file_path}")
            
        except Exception as e:
            self.logger.error(f"处理简历失败 {file_path}: {str(e)}")
            
    def run(self):
        """启动HR Agent"""
        self.logger.info("HR Agent 启动")
        
        # 处理现有文件
        unprocessed_files = self.file_watcher.get_unprocessed_files()
        for file_path in unprocessed_files:
            self.process_resume(file_path)
            
        # 开始监控新文件
        self.file_watcher.start_watching(self.process_resume)
        
if __name__ == "__main__":
    # 从环境变量或命令行参数获取配置文件路径
    config_path = os.getenv("HR_AGENT_CONFIG", "config.json")
    
    # 启动HR Agent
    agent = HRAgent(config_path)
    agent.run()