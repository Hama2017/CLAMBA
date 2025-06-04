from clamba.core import generate_slca_from_pdf

def test_generate_slca():
    slca = generate_slca_from_pdf("tests/contract.pdf", config_path="clamba.config.json")
    assert isinstance(slca, dict)
    print("SLCA généré avec succès :")
    print(slca)

test_generate_slca()