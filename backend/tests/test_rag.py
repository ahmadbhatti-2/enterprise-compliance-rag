from app.rag.chain import format_context


class DummyDocument:
    page_content = "Governance text"
    metadata = {"source": "AI_RMF_1.0.pdf", "page": 1}


def test_format_context_includes_source():
    context = format_context([DummyDocument()])
    assert "AI_RMF_1.0.pdf" in context
    assert "Governance text" in context
