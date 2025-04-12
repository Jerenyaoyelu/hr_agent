import json
import numpy as np
import os
import aiohttp
import asyncio
from langchain_openai import ChatOpenAI
from typing import List, Dict
from .llm.ollama_ds import OllamaDeepseek
from configparser import ConfigParser

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
        self.ds = OllamaDeepseek(config['deepseek']['model'])
        self.jd_desc = ''
        
    def load_jd(self, jd_text):
        # todo 后续可以考虑是否用特征向量效果更好
        # 使用DeepSeek生成岗位特征向量
        # prompt = f"请将以下岗位描述转换为特征向量描述：\n{jd_text}"
        # # response = self.llm.invoke(prompt)
        # self.jd_vector = self._text_to_vector(response.content)
        self.jd_desc = jd_text
        
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
    
    async def analyze_single_resume(self, session: aiohttp.ClientSession, resume_text: str) -> Dict:
        """
        分析单份简历
        """
        prompt = f"""请严格按JSON格式分析以下简历，包含以下字段：
        - skills (array): 关键技能（最多5个）
        - match_score (int): 与目标岗位的匹配度（0-100）
        - suggestions (array): 改进建议（最多3条）
        - summary (string): 100字内总结

        简历内容：
        {resume_text[:3000]}  # 限制输入长度

        目标岗位描述：
        {self.job_desc}

        要求：
        1. 从简历开头提取基本信息，缺失字段留空
        2. 手机号/邮箱需验证格式有效性
        3. 匹配度需结合岗位要求量化计算
        """

        raw_response = await self.ds.call_model(session, prompt)
        if not raw_response:
            return {"error": "模型调用失败"}

        try:
            # 清洗响应并解析JSON
            cleaned = raw_response.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        except json.JSONDecodeError:
            print("JSON解析失败，原始响应：", raw_response)
            return {"error": "响应格式无效"}

    async def batch_analyze(self, resumes: List[str]) -> List[Dict]:
        """
        批量分析简历
        """
        async with aiohttp.ClientSession() as session:
            tasks = [self.analyze_single_resume(session, text) for text in resumes]
            return await asyncio.gather(*tasks)

    def generate_report(self, results: List[Dict], output_file: str = "report.json"):
        """
        生成分析报告
        """
        # 数据清洗
        valid_results = [r for r in results if "error" not in r]

        # 生成统计信息
        stats = {
            "total_resumes": len(results),
            "valid_resumes": len(valid_results),
            "average_score": sum(r.get("match_score", 0) for r in valid_results) / len(valid_results) if valid_results else 0,
            "top_skills": self._get_common_skills(valid_results)
        }

        # 保存完整报告
        report = {
            "stats": stats,
            "details": valid_results
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"报告已生成：{output_file}")
        return report

    def _get_common_skills(self, results: List[Dict], top_n: int = 5) -> List[str]:
        skill_count = {}
        for res in results:
            for skill in res.get("skills", []):
                skill_count[skill] = skill_count.get(skill, 0) + 1
        return sorted(skill_count.items(), key=lambda x: x[1], reverse=True)[:top_n]