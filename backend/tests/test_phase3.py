import pytest
from app.services.calculations import financial_math

def test_ht_to_ttc_with_discount():
    res = financial_math.compute_ht_to_ttc(ht_amount=1000, tva_rate=20.0, discount_rate=10.0)
    assert res["is_valid"] is True
    assert res["details"]["net_ht"] == 900.0
    assert res["details"]["tva_amount"] == 180.0
    assert res["result"] == 1080.0

def test_margin_and_markup():
    res = financial_math.compute_margin_and_markup(cost_price=100, selling_price=150)
    assert res["is_valid"] is True
    assert res["result"] == 50.0
    assert res["details"]["margin_rate_pct"] == 50.0
    assert res["details"]["markup_rate_pct"] == 33.33

def test_budget_variance():
    res = financial_math.compute_budget_variance(budget_planned=10000, budget_actual=12000)
    assert res["is_valid"] is True
    assert res["result"] == 2000.0
    assert res["details"]["variance_pct"] == 20.0
    assert "Dépassement" in res["details"]["status"]

def test_compound_invoice():
    items = [
        {"label": "Prestation Audit", "quantity": 2, "unit_price": 1000.0, "tva_rate": 20.0, "discount_rate": 0.0},
        {"label": "Documentation", "quantity": 1, "unit_price": 500.0, "tva_rate": 5.5, "discount_rate": 10.0}
    ]
    res = financial_math.compute_compound_invoice(items)
    assert res["is_valid"] is True
    assert res["details"]["net_ht"] == 2450.0
    assert res["details"]["total_tva"] == 424.75
    assert res["result"] == 2874.75

def test_calculations_api_endpoint(client):
    payload = {
        "operation": "ht_to_ttc",
        "ht_amount": 5000,
        "tva_rate": 20.0,
        "discount_rate": 5.0,
        "currency": "EUR"
    }
    res = client.post("/api/v1/calculations/compute", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is True
    assert data["result"] == 5700.0
    assert data["id"] > 0
