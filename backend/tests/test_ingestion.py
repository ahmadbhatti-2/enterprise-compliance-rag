from app.ingestion.chunking import chunk_documents


class DummyDocument:
    def __init__(self, page_content: str):
        self.page_content = page_content
        self.metadata = {}


def test_chunk_documents_returns_chunks():
    chunks = chunk_documents([DummyDocument("This is a compliance test document.")])
    assert chunks
