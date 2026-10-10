import requests

def test_criar_investimento_sucesso(base_url, auth_headers):
    """
    Testa a criação de um investimento válido (POST /api/investments).
    Atribuição: Aluno 3
    """
    # 1. Dados válidos para a criação do investimento
    payload = {
        "asset_name": "CDB Pós-Fixado",
        "amount": 1000.00,
        "purchase_price": 1.00,
        "days_invested": 30,
        "planned_days": 365
    }
    
    # 2. Requisição POST para o endpoint
    response = requests.post(
        f"{base_url}/api/investments",
        json=payload,
        headers=auth_headers
    )
    
    # 3. Validação do status code esperado
    assert response.status_code == 201
