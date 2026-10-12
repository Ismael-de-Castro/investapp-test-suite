import requests


def pegar_ativo(base_url):
    return requests.get(f"{base_url}/api/assets").json()[0]


def test_listar_ativos_publicos(base_url):
    response = requests.get(f"{base_url}/api/assets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_ativos_possuem_campos_basicos(base_url):
    data = requests.get(f"{base_url}/api/assets").json()
    for ativo in data:
        assert "asset_name" in ativo
        assert "asset_type" in ativo
        assert "annual_rate" in ativo


def test_atualizar_taxa_ativo_sucesso(base_url, auth_headers):
    ativo = pegar_ativo(base_url)
    taxa_original = ativo["annual_rate"]

    response = requests.put(
        f"{base_url}/api/assets",
        json={"asset_name": ativo["asset_name"],
              "annual_rate": taxa_original + 0.1},
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text

    # restaura o valor original
    requests.put(
        f"{base_url}/api/assets",
        json={"asset_name": ativo["asset_name"],
              "annual_rate": taxa_original},
        headers=auth_headers,
    )


def test_atualizar_taxa_sem_token(base_url):
    ativo = pegar_ativo(base_url)
    response = requests.put(
        f"{base_url}/api/assets",
        json={"asset_name": ativo["asset_name"],
              "annual_rate": ativo["annual_rate"]},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_atualizar_taxa_payload_invalido(base_url, auth_headers):
    ativo = pegar_ativo(base_url)
    response = requests.put(
        f"{base_url}/api/assets",
        json={"asset_name": ativo["asset_name"], "annual_rate": "abc"},
        headers=auth_headers,
    )
    assert response.status_code == 422