from ingest_pdf import ingest_pdf

CHUNKS = ingest_pdf()
if __name__ == "__main__":
    print(f"全文片数为:{len(CHUNKS)}")  # 一共多少段
    print(CHUNKS[0]["id"], f"字数为:{len(CHUNKS[0]['text'])}")
    print(CHUNKS[0]["text"])
    print(CHUNKS[1]["id"], f"长度为:{len(CHUNKS[1]['text'])}")
    print(CHUNKS[1]["text"])
