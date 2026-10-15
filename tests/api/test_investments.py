import requests


def test_criar_investimento_poupanca_valido(base_url, auth_headers):
    """Cria um investimento válido em Poupança e espera HTTP 201."""
    payload = {
        "asset_name": "Poupança",
        "amount": 1000.00,
        "purchase_price": 1.00,
        "days_invested": 30,
        "planned_days": 365,
    }

    response = requests.post(
        f"{base_url}/api/investments",
        json=payload,
        headers=auth_headers,
    )

    print(f"\n[RESPOSTA] {response.status_code} -> {response.text}")

    assert response.status_code == 201


def test_criar_investimento_cdb_valido(base_url, auth_headers):
    """Cria um investimento válido em CDB e espera HTTP 201."""
    payload = {
        "asset_name": "CDB",
        "amount": 5000.00,
        "purchase_price": 1.00,
        "days_invested": 180,
        "planned_days": 720,
    }

    response = requests.post(
        f"{base_url}/api/investments",
        json=payload,
        headers=auth_headers,
    )

    print(f"\n[RESPOSTA] {response.status_code} -> {response.text}")

    assert response.status_code == 201
    data = response.json()
    assert data["asset_name"] == "CDB"
    assert data["amount"] == 5000.0


# ---------- INTEGRANTE 4: Listagem e Exclusão ----------

def _criar_investimento(base_url, auth_headers):
    """Helper: cria um investimento e retorna o JSON da resposta."""
    payload = {
        "asset_name": "Poupança",
        "amount": 1000.00,
        "purchase_price": 1.00,
        "days_invested": 30,
        "planned_days": 365,
    }
    response = requests.post(
        f"{base_url}/api/investments", json=payload, headers=auth_headers
    )
    assert response.status_code == 201
    return response.json()


def test_listar_investimentos(base_url, auth_headers):
    """Valida a listagem de investimentos do usuário autenticado."""
    criado = _criar_investimento(base_url, auth_headers)

    response = requests.get(f"{base_url}/api/investments", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert criado["id"] in [item["id"] for item in data]


def test_listar_investimentos_sem_token(base_url):
    """Valida que a listagem exige autenticação."""
    response = requests.get(f"{base_url}/api/investments")
    assert response.status_code in (401, 403)


def test_excluir_investimento(base_url, auth_headers):
    """Cria um investimento e o exclui com sucesso."""
    criado = _criar_investimento(base_url, auth_headers)
    investment_id = criado["id"]

    response = requests.delete(
        f"{base_url}/api/investments/{investment_id}", headers=auth_headers
    )
    assert response.status_code == 200

    lista = requests.get(f"{base_url}/api/investments", headers=auth_headers).json()
    assert investment_id not in [item["id"] for item in lista]


def test_excluir_investimento_inexistente(base_url, auth_headers):
    """Valida a exclusão de um ID que não existe."""
    response = requests.delete(
        f"{base_url}/api/investments/99999999", headers=auth_headers
    )
    assert response.status_code == 404
