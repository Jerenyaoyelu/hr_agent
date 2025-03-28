import shutil
from pathlib import Path
import json
from .parser import ResumeParser
from .evaluator import ResumeEvaluator

def process_resume(file_path):
    try:
        # 读取文件内容
        text = extract_text(file_path)
        
        # 解析简历
        parser = ResumeParser()
        parsed_data = parser.parse(text)
        if not parsed_data:
            raise ValueError("简历解析失败")
            
        # 评估简历
        evaluator = ResumeEvaluator()
        evaluator.load_jd(load_job_description())  # 从文件读取岗位描述
        evaluation = evaluator.evaluate(text)
        
        # 处理结果
        output = {
            "candidate": parsed_data,
            "evaluation": evaluation
        }
        
        # 保存结果
        save_output(file_path, output)
        
        # 归档文件
        archive_file(file_path)
        
    except Exception as e:
        handle_error(e, file_path)

def save_output(file_path, data):
    output_dir = Path("output/results")
    output_dir.mkdir(exist_ok=True)
    
    filename = file_path.stem + ".json"
    with open(output_dir / filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)