 import logging
from pathlib import Path
from typing import Dict, Any, Optional
import PyPDF2
import docx
import json
import openai
from dataclasses import dataclass, asdict

@dataclass
class ResumeData:
    name: str
    email: str
    phone: Optional[str]
    education: list
    work_experience: list
    skills: list
    projects: list
    certifications: Optional[list] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ResumeParser:
    def __init__(self, openai_api_key: str):
        """
        初始化简历解析器
        
        Args:
            openai_api_key: OpenAI API密钥
        """
        self.logger = logging.getLogger(__name__)
        openai.api_key = openai_api_key
        
    def _extract_text_from_pdf(self, file_path: Path) -> str:
        """从PDF文件中提取文本"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            self.logger.error(f"PDF解析错误: {str(e)}")
            raise
            
    def _extract_text_from_docx(self, file_path: Path) -> str:
        """从DOCX文件中提取文本"""
        try:
            doc = docx.Document(file_path)
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            self.logger.error(f"DOCX解析错误: {str(e)}")
            raise
            
    def _parse_text_with_llm(self, text: str) -> ResumeData:
        """使用LLM解析简历文本"""
        try:
            prompt = f"""请分析以下简历文本，并提取关键信息。请以JSON格式返回，包含以下字段：
            - name: 姓名
            - email: 邮箱
            - phone: 电话（如有）
            - education: 教育经历（列表）
            - work_experience: 工作经历（列表）
            - skills: 技能（列表）
            - projects: 项目经历（列表）
            - certifications: 证书（列表，如有）

            简历文本：
            {text}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一个专业的简历解析助手，请帮助提取简历中的关键信息。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            parsed_data = json.loads(response.choices[0].message.content)
            return ResumeData(**parsed_data)
            
        except Exception as e:
            self.logger.error(f"LLM解析错误: {str(e)}")
            raise
            
    def parse_resume(self, file_path: Path) -> ResumeData:
        """
        解析简历文件
        
        Args:
            file_path: 简历文件路径
            
        Returns:
            解析后的简历数据
        """
        try:
            # 根据文件扩展名选择相应的解析方法
            if file_path.suffix.lower() == '.pdf':
                text = self._extract_text_from_pdf(file_path)
            elif file_path.suffix.lower() in ['.doc', '.docx']:
                text = self._extract_text_from_docx(file_path)
            else:
                raise ValueError(f"不支持的文件格式: {file_path.suffix}")
                
            # 使用LLM解析文本
            resume_data = self._parse_text_with_llm(text)
            self.logger.info(f"成功解析简历: {file_path}")
            return resume_data
            
        except Exception as e:
            self.logger.error(f"简历解析失败 {file_path}: {str(e)}")
            raise