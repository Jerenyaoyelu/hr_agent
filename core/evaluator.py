from configparser import ConfigParser
import json
from langchain_openai import ChatOpenAI
import numpy as np
import os

class ResumeEvaluator:
    def __init__(self):
        config = ConfigParser()
        config.read('config/settings.yaml')
        
        self.llm = ChatOpenAI(
            openai_api_base=os.getenv("DEEPSEEK_API_BASE", config['deepseek']['api_base']),
            openai_api_key=os.getenv("DEEPSEEK_API_KEY", config['deepseek']['api_key']),
            model_name=config['deepseek']['model']
        )
        
        self.jd_vector = None
        
    def load_jd(self, jd_text):
        # 使用DeepSeek生成岗位特征向量
        prompt = f"请将以下岗位描述转换为特征向量描述：\n{jd_text}"
        response = self.llm.invoke(prompt)
        self.jd_vector = self._text_to_vector(response.content)
        
    def evaluate(self, resume_text):
        # 使用DeepSeek进行综合评估
        prompt = f"""
        根据以下简历内容评估是否符合岗位要求：
        简历内容：{resume_text[:2000]}  # 限制输入长度
        
        请返回JSON格式：
        {{
            "score": 0-100的评分,
            "reason": "评估理由",
            "match_points": ["匹配点1", "匹配点2"]
        }}
        """
        result = self.llm.invoke(prompt)
        return json.loads(result.content)
        
    def _text_to_vector(self, text):
        # 简单向量化方法（可替换为专业文本向量模型）
        return np.array([hash(text) % 100 for _ in range(128)])