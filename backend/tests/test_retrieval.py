from app.utils.citations import source_filter


def test_source_filter():
    assert source_filter("NIST_RMF.pdf") == {"source": "NIST_RMF.pdf"}
