
def test_simular_rendimento_mensal(base_url, auth_headers):
    """Testa a simulação de rendimento mensal para 12 meses."""

    payload = {
        "months": 12
    }

    response = requests.post(
        f"{base_url}/api/simulations/yield-monthly",
        json=payload,
        headers=auth_headers
    )

    assert response.status_code == 200
