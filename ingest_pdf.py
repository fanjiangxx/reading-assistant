import pymupdf


def ingest_pdf():
    doc_id = "2025年美的财务报告.pdf"
    pdf_path = r"D:\obsidian\试用\ai应用开发\finrag_min_hand\data\2025年美的财务报告.pdf"
    doc = pymupdf.open(pdf_path)
    def split_text(text, size=600, overlap=80):
        pieces = []
        start = 0
        total = len(text)
        while start < total:
            end = start + size
            if end > total:
                end = total
            piece = text[start:end]
            if piece.strip():
                pieces.append(piece)
            if end >= total:
                break
            start = end - overlap
            if start < 0:
                start = 0
        return pieces



    result = []
    n = 0
    for page_idx, page in enumerate(doc):
        page_text = page.get_text()
        for piece in split_text(page_text, size=600, overlap=80):
            n = n + 1
            item = {
                "id": f"midea_{n:03d}",
                "doc_id": doc_id,
                "page": page_idx + 1,
                "text": piece
            }
            result.append(item)
    doc.close()
    return result
