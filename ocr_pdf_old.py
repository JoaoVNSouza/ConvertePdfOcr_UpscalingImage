import os
import pytesseract
from pdf2image import convert_from_path
from pdf2image.pdf2image import pdfinfo_from_path
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
from pypdf import PdfReader, PdfWriter
import io
from dotenv import load_dotenv

# ===== CONFIG =====
load_dotenv()
POPPLER_PATH = os.environ.get("POPPLER_PATH")
TESSERACT_PATH = os.environ.get("TESSERACT_PATH")
DPI = int(os.environ.get("DPI"))
MAX_WORKERS = int(os.environ.get("MAX_WORKERS"))
TESSERACT_PREFIX = os.environ.get("TESSERACT_PREFIX")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# ===== FUNÇÕES =====
def process_page(page_number: int, PDF_PATH: str = None):
    """Processa uma única página e retorna (numero_pagina, bytes_pdf)"""

    pages = convert_from_path(
        PDF_PATH,
        dpi=DPI,
        poppler_path=POPPLER_PATH,
        first_page=page_number,
        last_page=page_number
    )

    page = pages[0]

    pdf_bytes = pytesseract.image_to_pdf_or_hocr(
        page,
        lang="por",
        extension="pdf"
    )

    return page_number, pdf_bytes


def ocr_pdf(PDF_PATH: str, OUTPUT_PATH: str = None):

    info = pdfinfo_from_path(PDF_PATH, poppler_path=POPPLER_PATH)
    total_pages = info["Pages"]
    results = {}

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(process_page, i, PDF_PATH): i
            for i in range(1, total_pages + 1)
        }

        for future in tqdm(as_completed(futures), total=total_pages, desc="OCR"):
            page_number, pdf_bytes = future.result()
            results[page_number] = pdf_bytes

    print("\nUnindo páginas corretamente...")
    writer = PdfWriter()

    for i in range(1, total_pages + 1):
        pdf_bytes = results[i]
        reader = PdfReader(io.BytesIO(pdf_bytes))
        writer.add_page(reader.pages[0])

    with open(f'{OUTPUT_PATH}/pdf_pesquisavel.pdf', "wb") as f:
        writer.write(f)

    print("PDF pesquisável criado com sucesso!")
