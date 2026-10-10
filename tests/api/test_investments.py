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