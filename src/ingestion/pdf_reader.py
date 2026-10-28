from pathlib import Path
from pypdf import PdfReader

def load_pdf(pdf_path):
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"Cannot find {pdf_path}")
    reader = PdfReader(pdf_path)
    pages = []
    for page_number,page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if not text or not text.strip():
            continue
        pages.append({"page": page_number, "text": text.strip(), "source": pdf_path.name})
    return pages
if __name__ == "__main__":
    result = load_pdf("Data/papers/raw/Lesson01-Introduction.pdf")
    print("Pages with text:", len(result))
    print(result[0]["text"][:100])
    