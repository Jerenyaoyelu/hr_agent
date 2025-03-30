from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json
from config.config_loader import load_config
from core.deepseek_llm import DeepSeekLLM  # 假设自定义类放在 core/deepseek_llm.py

class ResumeParser:
    def __init__(self):
        config = load_config()
        print('config', config)
        self.llm = DeepSeekLLM(
            api_base=config['deepseek']['api_base'],
            api_key=config['deepseek']['api_key'],
            model_name=config['deepseek']['model'],
            temperature=0.1
        )
        print(self.llm._llm_type)
        self.prompt = ChatPromptTemplate.from_template("""
        [角色] 你是专业招聘专家
        [任务] 从简历内容提取结构化信息：
        ---
        {resume_text}
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
            }}
        }}
        2. 没有明确信息时填写null
        3. 工作年限按数值类型返回
        """)

    def parse(self, text):
        try:
            chain = self.prompt | self.llm
            print('chain', chain)
            result = chain.invoke({"resume_text": text})
            return self._validate_json(result.content)
        except Exception as e:
            print(f"解析失败: {str(e)}")
            return None
            
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