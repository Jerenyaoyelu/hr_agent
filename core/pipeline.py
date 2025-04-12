import shutil
from pathlib import Path
import json
import asyncio
import aiohttp
from core.text_extractor import extract_text_pages
from .parser import ResumeParser
from .evaluator import ResumeEvaluator

async def process_resume(file_path):
    try:
        # 读取文件内容
        text = extract_text_pages(file_path)
        # 解析简历
        parser = ResumeParser()
        async with aiohttp.ClientSession() as session:
            parsed_data = await parser.parse(session,text)
        if not parsed_data:
            raise ValueError("简历解析失败")
        # 打印解析后的数据
        print("Parsed Data:", parsed_data)
        # 评估简历
        evaluator = ResumeEvaluator()
        evaluator.load_jd(load_job_description())  # 从文件读取岗位描述
        results = await asyncio.run(evaluator.batch_analyze([parsed_data]))
         # 生成报告
        report = evaluator.generate_report(results, "resume_report.json")
        # # 处理结果
        # output = {
        #     "candidate": parsed_data,
        #     "evaluation": evaluation
        # }
        
        # 保存结果
        # save_output(file_path, output)
        print(report)
        
        # 归档文件
        archive_file(file_path)
        
    except Exception as e:
        print('报错了',e)
        handle_error(e, file_path)

def save_output(file_path, data):
    output_dir = Path("output/results")
    output_dir.mkdir(exist_ok=True)
    
    filename = file_path.stem + ".json"
    with open(output_dir / filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_job_description():
    """
    从文件中加载岗位描述。
    假设岗位描述存储在 'config/job_description.json' 文件中。
    """
    job_description_path = Path("config/job_description.json")
    if not job_description_path.exists():
        raise FileNotFoundError(f"岗位描述文件未找到: {job_description_path}")
    
    with open(job_description_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def archive_file(file_path):
    """
    将处理过的文件移动到归档目录。
    假设归档目录为 'output/archive'。
    """
    archive_dir = Path("output/archive")
    archive_dir.mkdir(exist_ok=True)  # 如果目录不存在，则创建

    # 移动文件到归档目录
    destination = archive_dir / file_path.name
    shutil.move(str(file_path), str(destination))
    print(f"文件已归档到: {destination}")

def handle_error(exception, file_path):
    """
    处理错误，将错误信息记录到日志文件，并将出错的文件移动到错误目录。
    """
    error_dir = Path("output/errors")
    error_dir.mkdir(exist_ok=True)  # 如果目录不存在，则创建

    # 记录错误日志
    log_file = error_dir / "error.log"
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"Error processing file {file_path}:\n")
        log.write(f"{exception}\n")
        log.write("-" * 40 + "\n")

    # 将出错的文件移动到错误目录
    destination = error_dir / file_path.name
    shutil.move(str(file_path), str(destination))
    print(f"文件 {file_path} 处理失败，已移动到: {destination}")