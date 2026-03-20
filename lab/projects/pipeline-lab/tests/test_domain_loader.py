from app.services.domain_loader import load_domain, list_domains


def test_domain_loader_reads_spec():
    domains = list_domains()
    assert any("python.yaml" in path.name for path in domains)
    assert load_domain("python")["name"] == "python"
