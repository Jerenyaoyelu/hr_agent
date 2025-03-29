import fitz  # PyMuPDF
from pathlib import Path

def extract_text(file_path):
    """
    使用 PyMuPDF 从 PDF 文件中提取文本。
    """
    file_path = Path(file_path)
    if file_path.suffix.lower() != ".pdf":
        raise ValueError(f"Unsupported file format: {file_path}")

    print(f"Processing file: {file_path}")

    try:
        # 打开 PDF 文件
        with fitz.open(file_path) as pdf:
            text = ""
            for page_num in range(len(pdf)):
                page = pdf[page_num]
                text += page.get_text() + "\n"  # 提取每一页的文本并换行
            return text.strip()
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from {file_path}: {e}")