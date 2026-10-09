from ingest_pdf import ingest_pdf

CHUNKS = ingest_pdf()
if __name__ == "__main__":
    print(CHUNKS)

