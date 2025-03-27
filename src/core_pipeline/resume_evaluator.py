import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import openai
from dataclasses import dataclass
import numpy as np
from .resume_parser import ResumeData

@dataclass
class JobRequirement:
    title: str
    required_skills: List[str]
    preferred_skills: List[str]
    minimum_years_experience: int
    education_requirement: str
    job_description: str

@dataclass
class EvaluationResult:
    score: float  # 0-100
    matching_skills: List[str]
    missing_skills: List[str]
    experience_match: bool
    education_match: bool
    detailed_feedback: str
    recommendation: str

class ResumeEvaluator:
    def __init__(self, openai_api_key: str):
        """
        初始化简历评估器
        
        Args:
            openai_api_key: OpenAI API密钥
        """
        self.logger = logging.getLogger(__name__)
        openai.api_key = openai_api_key
        
    def _calculate_skill_match_score(self, resume_skills: List[str], required_skills: List[str], 
                                   preferred_skills: List[str]) -> tuple[float, List[str], List[str]]:
        """计算技能匹配分数"""
        # 将技能转换为小写以进行不区分大小写的比较
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        required_skills_lower = [skill.lower() for skill in required_skills]
        preferred_skills_lower = [skill.lower() for skill in preferred_skills]
        
        # 计算匹配的必需技能
        matching_required = [skill for skill in required_skills
                           if skill.lower() in resume_skills_lower]
        
        # 计算匹配的优先技能
        matching_preferred = [skill for skill in preferred_skills
                            if skill.lower() in resume_skills_lower]
        
        # 计算缺失的必需技能
        missing_skills = [skill for skill in required_skills
                         if skill.lower() not in resume_skills_lower]
        
        # 计算得分
        required_score = len(matching_required) / len(required_skills) * 70
        preferred_score = (len(matching_preferred) / len(preferred_skills) * 30 
                         if preferred_skills else 30)
        
        total_score = required_score + preferred_score
        return total_score, matching_required + matching_preferred, missing_skills
        
    def _evaluate_with_llm(self, resume_data: ResumeData, job_requirement: JobRequirement) -> str:
        """使用LLM进行详细评估"""
        try:
            prompt = f"""请根据以下信息评估候选人是否适合该职位，并提供详细的分析和建议：

            职位信息：
            - 职位名称：{job_requirement.title}
            - 职位描述：{job_requirement.job_description}
            - 要求工作经验：{job_requirement.minimum_years_experience}年
            - 学历要求：{job_requirement.education_requirement}

            候选人信息：
            - 教育背景：{resume_data.education}
            - 工作经验：{resume_data.work_experience}
            - 技能：{resume_data.skills}
            - 项目经历：{resume_data.projects}
            - 证书：{resume_data.certifications}

            请提供：
            1. 候选人优势分析
            2. 潜在风险或不足
            3. 是否建议进入面试环节
            4. 建议面试重点关注的方面
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一个专业的HR助理，请帮助评估候选人是否适合职位。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"LLM评估错误: {str(e)}")
            raise
            
    def evaluate_resume(self, resume_data: ResumeData, 
                       job_requirement: JobRequirement) -> EvaluationResult:
        """
        评估简历是否符合职位要求
        
        Args:
            resume_data: 解析后的简历数据
            job_requirement: 职位要求
            
        Returns:
            评估结果
        """
        try:
            # 计算技能匹配度
            score, matching_skills, missing_skills = self._calculate_skill_match_score(
                resume_data.skills,
                job_requirement.required_skills,
                job_requirement.preferred_skills
            )
            
            # 检查工作经验是否满足要求
            total_experience = sum(len(exp) for exp in resume_data.work_experience)
            experience_match = total_experience >= job_requirement.minimum_years_experience
            
            # 检查学历是否满足要求
            education_match = any(
                job_requirement.education_requirement.lower() in edu.lower() 
                for edu in resume_data.education
            )
            
            # 获取LLM的详细评估
            detailed_feedback = self._evaluate_with_llm(resume_data, job_requirement)
            
            # 生成建议
            if score >= 80 and experience_match and education_match:
                recommendation = "强烈建议面试"
            elif score >= 60 and (experience_match or education_match):
                recommendation = "建议面试，但需要关注部分不足"
            else:
                recommendation = "暂不建议面试"
            
            return EvaluationResult(
                score=score,
                matching_skills=matching_skills,
                missing_skills=missing_skills,
                experience_match=experience_match,
                education_match=education_match,
                detailed_feedback=detailed_feedback,
                recommendation=recommendation
            )
            
        except Exception as e:
            self.logger.error(f"简历评估失败: {str(e)}")
            raise