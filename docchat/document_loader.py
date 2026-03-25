from pypdf import PdfReader


def load_pdf(path):
    reader = PdfReader(path)
    pages = []

    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text()

        if text and text.strip():
            pages.append(
                {
                    "text": text,
                    "page": page_num,
                    "source": path,
                }
            )

    return pages

