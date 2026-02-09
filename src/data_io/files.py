from config import MAX_FILE_CHARS
import os
import mimetypes
from typing import Optional


def _safe_trimming(input_txt: str, limit: int = MAX_FILE_CHARS) -> str:
    """Trim(Truncate) input text if it over limit.

    Args:
        input_txt (str): The input text from human or ai
        limit (int, optional): Max length of character that want to be shown. Defaults to MAX_FILE_CHARS.

    Returns:
        str: Truncated string
    """

    res = input_txt or ""
    if len(res) <= limit:
        return res
    else:
        res = input_txt[:limit] + "\n\n...[TRUNCATED]..."
        return res


def extract_text_from_file(file_path: str) -> tuple[Optional[str], str]:
    res = (None, "")

    if not file_path or not os.path.exists(file_path):
        print(f"There is no file exist in {file_path}")
        return res
    mime, _ = mimetypes.guess_type(file_path)
    f_type = os.path.splitext(file_path)[1].lower()

    try:
        if f_type in [".txt", ".md", ".log", ".csv", ".json", ".yaml", ".yml"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
                res = (None, _safe_trimming(fh.read()))
        elif f_type in [".xlsx", ".xls"]:
            try:
                import pandas as pd

                xls = pd.ExcelFile(file_path)
                parts: list[str] = list()
                for sheet_name in xls.sheet_names[:2]:
                    df = xls.parse(sheet_name).head(50)
                    parts.append(f'[sheet: {sheet_name}]\n{df.to_csv(index=False, sep='\t')}')
                res = (None, _safe_trimming("\n\n".join(parts)))
            except Exception as e:
                res = (None, f"Excel file read error: {e}")
        elif f_type == ".pdf":
            try:
                from pypdf import PdfReader

                reader = PdfReader(file_path)
                pdf_texts = list()
                for page_num, page in enumerate(reader.pages[:10], start=1):
                    txt_get = page.extract_text() or ""
                    if txt_get.strip():
                        pdf_texts.append(f"[Page {page_num}]: {txt_get}")
                joined_pdf_txt = "\n\n".join(pdf_texts).strip()
                res = (
                    file_path,
                    _safe_trimming(
                        joined_pdf_txt
                        if joined_pdf_txt
                        else "PDF 추출 결과가 비어있습니다. 혹은 이미지 pdf로 보여집니다."
                    ),
                )
            except Exception as e:
                res = (file_path, f"[PDF read error] {e}\n pypdf 설치가 필요합니다")
        else:
            res = (None, "지원하지 않는 파일 형식입니다. txt/csv/xlsx/pdf 업로드를 권장합니다.")

    except Exception as e:
        res = (None, f"File read error {e}")

    return res


def update_file_context(files: list) -> str:
    """Store text what was extracted from input files

    Args:
        files (list): A list of input files. They could be PDF or text.

    Returns:
        str: Extracted text from files.
    """

    res = ""

    if not files:
        return res

    parts = list()
    for file in files:
        file_path = (
            getattr(file, "path", None) or getattr(file, "name", None) or (file if isinstance(file, str) else None)
        )
        if not file_path:
            continue
        file_type = (file_path.split(".")[-1] or "").lower()
        if file_type in ["pdf", "xlsx", "xls", "txt", "csv", "json", "md", "log", "yaml", "yml"]:
            _, txt = extract_text_from_file(file_path)
            if txt and txt.strip():
                parts.append(f"[{os.path.basename(file_path)}]\n{txt}")

    res = "\n\n".join(parts).strip()

    return res


def update_preview_and_context(multi_modal: dict) -> tuple[str, str, str]:
    """Process a Gardio multimodal textbox input to update pdf preview and file context.

    Args:
        multi_modal (dict): Input from Gardio MultimodalTextbox.

    Returns:
        tuple[str, str, str]: A tuple containing pdf path, extracted text, file context.
    """

    res = ("", "", "")

    files = (multi_modal or {}).get("files") or list()
    extracted_txt = update_file_context(files)

    pdf_path = None
    for file in reversed(files):
        file_path = (
            getattr(file, "path", None) or getattr(file, "name", None) or (file if isinstance(file, str) else None)
        )
        if file_path and file_path.lower().endswith(".pdf"):
            pdf_path = file_path
            break

    res = (pdf_path, extracted_txt, extracted_txt)

    return res


def sync_histories(history: list) -> str:
    """Render chat history to a single markdown/text blob.

    Args:
        history (list): The chat history

    Returns:
        str: Rendered chat history
    """

    res = ""

    if not history:
        res = "아직 대화가 없습니다."
    lines: list[str] = list()
    if isinstance(history[0], dict) and "role" in history[0]:
        for msg in history:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                lines.append(f"You: {content}")
            elif role == "assitant":
                lines.append(f"Bot: {content}")
    res = "\n\n".join(lines) if lines else "아직 대화가 없습니다."

    return res
