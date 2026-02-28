from pypdf import PdfReader
import sys
sys.stdout.reconfigure(encoding='utf-8')
def load_pdf(path):
    reader = PdfReader(path)
    pages = []

    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()

        if text and text.strip():
            pages.append({
                "text": text,
                "page": page_num + 1,
                "source": path
            })

    return pages
# res = load_pdf("CoverLetter.pdf")
# print(f"Extracted text length: {len(res)} characters")
# print(res[:500])  # Print the first 500 characters of the extracted text
# print(res)



