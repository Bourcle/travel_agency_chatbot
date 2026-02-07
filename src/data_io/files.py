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
