import pytest
import requests

ENDPOINT = "/api/simulate/yield-monthly"


def simular(base_url, headers, months=12):
    """Chama o endpoint de simulação de rendimento mensal."""
    return requests.post(
        f"{base_url}{ENDPOINT}", json={"months": months}, headers=headers
    )


# ---------- INTEGRANTE 5: simulação de rendimento mensal ----------

def test_simular_rendimento_mensal(base_url, auth_headers):
    """Simulação de 12 meses retorna 200."""
    response = simular(base_url, auth_headers, 12)
    print(f"\n[YIELD] status={response.status_code}")
    assert response.status_code == 200


def test_yield_monthly_estrutura_resposta(base_url, auth_headers):
    """A resposta traz todas as chaves esperadas, nos três níveis."""
    data = simular(base_url, auth_headers, 12).json()

    for chave in (
        "monthly_breakdown",
        "type_summary",
        "total_portfolio_invested",
        "total_portfolio_future",
        "total_portfolio_profit",
        "total_portfolio_growth_pct",
    ):
        assert chave in data, f"Chave ausente na resposta: {chave}"

    mes = data["monthly_breakdown"][0]
    assert {"month", "assets", "total_month_value"} <= set(mes)

    ativo = mes["assets"][0]
    assert {"asset_name", "asset_type", "projected_value",
            "monthly_growth_pct"} <= set(ativo)

    resumo = data["type_summary"][0]
    assert {"asset_type", "total_invested", "total_final_value",
            "total_profit", "growth_pct", "share_pct"} <= set(resumo)


@pytest.mark.parametrize("months", [1, 6, 12, 24, 36])
def test_yield_monthly_varios_prazos(base_url, auth_headers, months):
    """O breakdown tem exatamente um item por mês, numerado de 1 a N."""
    response = simular(base_url, auth_headers, months)
    assert response.status_code == 200

    breakdown = response.json()["monthly_breakdown"]
    assert len(breakdown) == months
    assert [m["month"] for m in breakdown] == list(range(1, months + 1))


def test_yield_monthly_prazo_padrao(base_url, auth_headers):
    """Sem o campo months, a API assume 12 meses (default do schema)."""
    response = requests.post(
        f"{base_url}{ENDPOINT}", json={}, headers=auth_headers
    )
    assert response.status_code == 200
    assert len(response.json()["monthly_breakdown"]) == 12


def test_yield_monthly_total_cresce_ao_longo_dos_meses(base_url, auth_headers):
    """Regra de negócio: com taxas positivas, o total nunca diminui."""
    breakdown = simular(base_url, auth_headers, 24).json()["monthly_breakdown"]
    totais = [m["total_month_value"] for m in breakdown]
    assert all(a <= b for a, b in zip(totais, totais[1:])), totais


def test_yield_monthly_crescimento_dos_ativos_positivo(base_url, auth_headers):
    """Cada ativo deve ter crescimento mensal percentual positivo."""
    breakdown = simular(base_url, auth_headers, 12).json()["monthly_breakdown"]
    for mes in breakdown:
        for ativo in mes["assets"]:
            assert ativo["monthly_growth_pct"] > 0, ativo


def test_yield_monthly_total_do_mes_igual_soma_dos_ativos(base_url, auth_headers):
    """total_month_value deve ser a soma dos projected_value (tolerância de arredondamento)."""
    breakdown = simular(base_url, auth_headers, 12).json()["monthly_breakdown"]
    for mes in breakdown:
        soma = sum(a["projected_value"] for a in mes["assets"])
        assert mes["total_month_value"] == pytest.approx(soma, abs=1.0), mes["month"]


def test_yield_monthly_futuro_igual_ao_ultimo_mes(base_url, auth_headers):
    """total_portfolio_future deve coincidir com o total do último mês simulado."""
    data = simular(base_url, auth_headers, 12).json()
    ultimo = data["monthly_breakdown"][-1]["total_month_value"]
    assert data["total_portfolio_future"] == pytest.approx(ultimo, abs=0.01)


def test_yield_monthly_lucro_igual_futuro_menos_investido(base_url, auth_headers):
    """Lucro do portfólio = valor futuro - valor investido."""
    data = simular(base_url, auth_headers, 12).json()
    esperado = data["total_portfolio_future"] - data["total_portfolio_invested"]
    assert data["total_portfolio_profit"] == pytest.approx(esperado, abs=0.01)


def test_yield_monthly_resumo_por_tipo_consistente(base_url, auth_headers):
    """type_summary deve fechar com os totais do portfólio."""
    data = simular(base_url, auth_headers, 12).json()
    resumo = data["type_summary"]

    investido = sum(t["total_invested"] for t in resumo)
    assert investido == pytest.approx(data["total_portfolio_invested"], abs=0.01)

    assert sum(t["share_pct"] for t in resumo) == pytest.approx(100, abs=0.1)

    for t in resumo:
        lucro = t["total_final_value"] - t["total_invested"]
        assert t["total_profit"] == pytest.approx(lucro, abs=0.01), t["asset_type"]


def test_yield_monthly_months_com_tipo_invalido(base_url, auth_headers):
    """months não numérico deve ser rejeitado pela validação (422)."""
    response = requests.post(
        f"{base_url}{ENDPOINT}", json={"months": "abc"}, headers=auth_headers
    )
    assert response.status_code == 422


def test_yield_monthly_sem_autenticacao(base_url):
    """Sem token, o endpoint recusa o acesso."""
    response = requests.post(f"{base_url}{ENDPOINT}", json={"months": 12})
    assert response.status_code in (401, 403)
