from pypdf import PdfReader
from pathlib import Path
from docx import Document
import win32com.client  # 用于处理 .doc 文件

def extract_text_pages(file_path):
    """
    根据文件类型（PDF、DOC 或 DOCX）提取文本。
    """
    file_path = Path(file_path).resolve()  # 转换为绝对路径
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    print(f"Processing file: {file_path}")

    try:
        if file_path.suffix.lower() == ".pdf":
            # 使用 PyPDF2 提取 PDF 文本
            text = extract_pdf_text(file_path)
            # print('result', text)
        elif file_path.suffix.lower() == ".docx":
            # 使用 python-docx 提取 DOCX 文本
            text = extract_docx_text(file_path)
        elif file_path.suffix.lower() == ".doc":
            # 使用 pywin32 提取 DOC 文本
            text = extract_doc_text(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        if not text:
            raise ValueError(f"No text found in the file: {file_path}")
        return text
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from {file_path}: {e}")

def extract_pdf_text(file_path):
    """
    使用 PyPDF2 从 PDF 文件中提取文本。
    """
    try:
        reader = PdfReader(str(file_path))
        number_of_pages = len(reader.pages)
        print(number_of_pages)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""  # 提取每一页的文本
            # print(f"Page {page_num + 1} content:\n{text}\n")
        return text
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF file {file_path}: {e}")

def extract_docx_text(file_path):
    """
    使用 python-docx 从 DOCX 文件中提取文本。
    """
    try:
        # 确保文件路径是字符串并以 UTF-8 编码处理
        file_path = str(file_path)
        doc = Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from DOCX file {file_path}: {e}")

def extract_doc_text(file_path):
    """
    使用 pywin32 从 DOC 文件中提取文本。
    """
    word = None
    try:
        # 启动 Word 应用程序
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        doc = word.Documents.Open(str(file_path))
        text = doc.Content.Text
        doc.Close()
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from DOC file {file_path}: {e}")
    finally:
        # 确保 Word 应用程序在任何情况下都能关闭
        if word:
            word.Quit()