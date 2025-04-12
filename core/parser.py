import json
import aiohttp
from config.config_loader import load_config
from .llm.ollama_ds import OllamaDeepseek

class ResumeParser:
    def __init__(self):
        config = load_config()
        print('config', config)
        self.ds = OllamaDeepseek(config['deepseek']['model'])
        self.resume_text = ""  # 初始化 resume_text

    def generate_prompt(self):
        return f"""
        [角色] 你是专业招聘专家
        [任务] 从简历内容提取结构化信息：
        ---
        {self.resume_text}
        ---
        
        [输出要求]
        1. 严格使用以下JSON格式：
        {{
            "name": "姓名（必填）",
            "contact": {{
            "email": "邮箱",
            "phone": "手机号"
            }},
            "skills": ["技能1", "技能2"],
            "experience_years": 工作年限,
            "education": {{
            "degree": "学历",
            "school": "毕业院校"
            }},
            "personal_evaluation": "个人评价",
            "work_experience": [
            {{
                "company": "公司名称",
                "position": "职位",
                "duration": "工作时长",
                "description": "工作描述"
            }}
            ]
        }}
        2. 没有明确信息时填写null
        3. 工作年限按数值类型返回
        """

    async def parse(self, session: aiohttp.ClientSession, text:str):
        self.resume_text = text
        raw_response = await self.ds.call_model(session, self.generate_prompt())
        if not raw_response:
            return {"error": "模型调用失败"}
        try:
            # 清洗响应并解析JSON
            cleaned = raw_response.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        except json.JSONDecodeError:
            print("JSON解析失败，原始响应：", raw_response)
            return {"error": "响应格式无效"}
            
    def _validate_json(self, raw):
        try:
            data = json.loads(raw)
            # 强制校验必要字段
            if not data.get("name"):
                raise ValueError("姓名字段缺失")
            return data
        except json.JSONDecodeError:
            # 自动修正常见格式错误
            corrected = raw.replace("'", '"').replace("None", "null")
            return json.loads(corrected)