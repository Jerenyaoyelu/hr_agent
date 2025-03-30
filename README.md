# HR Agent - 智能简历处理和面试调度系统

这是一个基于人工智能的 HR 助手系统，可以自动处理简历、评估候选人、安排面试并生成分析报告。

## 功能特点

- 自动监控指定文件夹中的新简历文件
- 支持 PDF、DOC、DOCX 格式的简历解析
- 使用 GPT-4 进行智能简历分析和评估
- 自动匹配职位要求和候选人技能
- 智能调度面试时间
- 自动发送面试邀请邮件
- 生成评估报告和数据分析

## 系统架构

系统分为三层：

1. 输入层：负责监控和接收简历文件
2. 核心处理流水线：
   - 简历解析引擎
   - 智能评估中心
   - 面试调度器
3. 输出层：负责结果持久化和通知

## 安装要求

- Python 3.8+
- OpenAI API 密钥
- SMTP 服务器（用于发送邮件通知）

## 安装步骤

1. 克隆代码库：

   ```bash
   git clone https://github.com/yourusername/hr-agent.git
   cd hr-agent
   ```

2. 创建虚拟环境：

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

4. 配置系统：
   - 复制 `config.json.example` 为 `config.json`
   - 修改配置文件中的相关设置：
     - OpenAI API 密钥
     - 监控文件夹路径
     - SMTP 服务器设置
     - 职位要求
     - 面试官信息

## 使用方法

1. 启动系统：

   ```bash
   - .\venv\Scripts\Activate.ps1
   - python src/main.py
   ```

2. 将简历文件放入监控文件夹中，系统将自动开始处理

3. 查看输出：
   - 处理结果将保存在配置的输出目录中
   - 日志文件记录了详细的处理过程
   - 符合要求的候选人将收到面试邀请邮件

## 目录结构

```
hr-agent/
├── src/
│   ├── input_layer/
│   │   └── file_watcher.py
│   ├── core_pipeline/
│   │   ├── resume_parser.py
│   │   ├── resume_evaluator.py
│   │   └── interview_scheduler.py
│   ├── output_layer/
│   │   └── persistence.py
│   └── main.py
├── config.json
├── requirements.txt
├── README.md
├── resumes/        # 简历文件夹
├── output/         # 输出目录
└── logs/           # 日志目录
```

## 配置说明

配置文件 `config.json` 包含以下主要设置：

- `watch_dir`: 监控的简历文件夹路径
- `output_dir`: 输出目录路径
- `log_file`: 日志文件路径
- `supported_extensions`: 支持的文件格式
- `openai_api_key`: OpenAI API 密钥
- `job_requirement`: 职位要求配置
- `interviewers`: 面试官信息
- `smtp_config`: 邮件服务器配置

## 注意事项

- 请确保 OpenAI API 密钥和 SMTP 服务器配置正确
- 建议定期备份输出目录中的数据
- 系统日志对排查问题很有帮助
- 可以根据需要调整职位要求和评估标准

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进系统。在提交代码前，请确保：

1. 代码符合 PEP 8 规范
2. 添加了适当的注释和文档
3. 通过了所有测试

## 许可证

MIT License
