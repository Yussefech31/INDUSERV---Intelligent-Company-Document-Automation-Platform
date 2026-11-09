from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional

TWO_PLACES = Decimal("0.01")
FOUR_PLACES = Decimal("0.0001")

def to_decimal(val: Any) -> Decimal:
    """Safely convert any numeric input or string to Decimal."""
    if val is None:
        raise ValueError("Missing numeric value: None cannot be converted to Decimal.")
    if isinstance(val, (int, float, str)):
        return Decimal(str(val))
    if isinstance(val, Decimal):
        return val
    raise ValueError(f"Unsupported type for Decimal conversion: {type(val)}")

def round_currency(val: Decimal) -> Decimal:
    """Rounds to 2 decimal places using standard financial ROUND_HALF_UP."""
    return val.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

def compute_ht_to_ttc(
    ht_amount: Any,
    tva_rate: Any = 20.0,
    discount_rate: Any = 0.0,
    currency: str = "EUR"
) -> Dict[str, Any]:
    """
    Computes HT (Hors Taxe) -> Discount -> Net HT -> TVA -> TTC (Toutes Taxes Comprises).
    """
    ht = to_decimal(ht_amount)
    tva_pct = to_decimal(tva_rate)
    disc_pct = to_decimal(discount_rate)

    if ht < 0:
        raise ValueError("Le montant HT ne peut pas être négatif.")

    # Discount
    discount_amount = round_currency(ht * (disc_pct / Decimal("100")))
    net_ht = ht - discount_amount

    # TVA
    tva_amount = round_currency(net_ht * (tva_pct / Decimal("100")))

    # TTC
    ttc = net_ht + tva_amount

    formula = f"Net_HT = {ht} - {discount_amount} (remise {disc_pct}%); TVA ({tva_pct}%) = {tva_amount}; TTC = {net_ht} + {tva_amount}"

    return {
        "operation": "ht_to_ttc",
        "inputs": {
            "ht_amount": float(ht),
            "tva_rate_pct": float(tva_pct),
            "discount_rate_pct": float(disc_pct),
            "currency": currency
        },
        "formula": formula,
        "result": float(ttc),
        "currency_or_unit": currency,
        "is_valid": True,
        "details": {
            "initial_ht": float(ht),
            "discount_amount": float(discount_amount),
            "net_ht": float(net_ht),
            "tva_amount": float(tva_amount),
            "total_ttc": float(ttc),
            "rounding_method": "ROUND_HALF_UP (2 décimales légales)"
        }
    }

def compute_margin_and_markup(
    cost_price: Any,
    selling_price: Any,
    currency: str = "EUR"
) -> Dict[str, Any]:
    """
    Computes gross margin (Marge Brute), margin rate (Taux de marge), and markup rate (Taux de marque).
    Marge brute = PV HT - PR
    Taux de marge = (Marge / PR) * 100
    Taux de marque = (Marge / PV) * 100
    """
    pr = to_decimal(cost_price)
    pv = to_decimal(selling_price)

    if pr <= 0:
        raise ValueError("Le coût d'achat / prix de revient doit être strictement positif.")
    if pv <= 0:
        raise ValueError("Le prix de vente doit être strictement positif.")

    gross_margin = round_currency(pv - pr)
    margin_rate_pct = ((gross_margin / pr) * Decimal("100")).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    markup_rate_pct = ((gross_margin / pv) * Decimal("100")).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    formula = f"Marge = {pv} - {pr}; Taux Marge = (Marge/{pr})*100; Taux Marque = (Marge/{pv})*100"

    return {
        "operation": "margin_and_markup",
        "inputs": {
            "cost_price": float(pr),
            "selling_price": float(pv),
            "currency": currency
        },
        "formula": formula,
        "result": float(gross_margin),
        "currency_or_unit": currency,
        "is_valid": True,
        "details": {
            "gross_margin": float(gross_margin),
            "margin_rate_pct": float(margin_rate_pct),
            "markup_rate_pct": float(markup_rate_pct),
            "is_profitable": gross_margin > 0
        }
    }

def compute_budget_variance(
    budget_planned: Any,
    budget_actual: Any,
    currency: str = "EUR"
) -> Dict[str, Any]:
    """
    Computes budget variance (Écart Budgétaire).
    Écart = Réel - Prévu
    Écart % = ((Réel - Prévu) / Prévu) * 100
    """
    planned = to_decimal(budget_planned)
    actual = to_decimal(budget_actual)

    if planned == 0:
        raise ValueError("Le budget prévu ne peut pas être nul pour calculer un pourcentage d'écart.")

    variance_val = round_currency(actual - planned)
    variance_pct = ((variance_val / abs(planned)) * Decimal("100")).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    formula = f"Écart = {actual} - {planned} ({variance_val} {currency}); Écart % = ({variance_val} / |{planned}|) * 100"

    return {
        "operation": "budget_variance",
        "inputs": {
            "budget_planned": float(planned),
            "budget_actual": float(actual),
            "currency": currency
        },
        "formula": formula,
        "result": float(variance_val),
        "currency_or_unit": currency,
        "is_valid": True,
        "details": {
            "variance_amount": float(variance_val),
            "variance_pct": float(variance_pct),
            "status": "Dépassement (Over-budget)" if variance_val > 0 else "Économie (Under-budget)" if variance_val < 0 else "Conforme"
        }
    }

def compute_compound_invoice(
    items: List[Dict[str, Any]],
    currency: str = "EUR"
) -> Dict[str, Any]:
    """
    Computes a multi-item invoice or tender price schedule with individual quantities,
    unit prices, line discounts, line TVA rates, and aggregate totals.
    """
    if not items:
        raise ValueError("La liste des articles ne peut pas être vide.")

    line_details = []
    total_ht = Decimal("0.00")
    total_discount = Decimal("0.00")
    total_tva = Decimal("0.00")
    tva_by_rate: Dict[str, Decimal] = {}

    for idx, item in enumerate(items):
        label = item.get("label", f"Article {idx + 1}")
        qty = to_decimal(item.get("quantity", 1))
        unit_price = to_decimal(item.get("unit_price") if item.get("unit_price") is not None else item.get("amount", 0))
        tva_pct = to_decimal(item.get("tva_rate", 20.0))
        disc_pct = to_decimal(item.get("discount_rate", 0.0))

        gross_line_ht = round_currency(qty * unit_price)
        line_disc = round_currency(gross_line_ht * (disc_pct / Decimal("100")))
        net_line_ht = gross_line_ht - line_disc
        line_tva = round_currency(net_line_ht * (tva_pct / Decimal("100")))
        line_ttc = net_line_ht + line_tva

        total_ht += gross_line_ht
        total_discount += line_disc
        total_tva += line_tva

        rate_key = f"{tva_pct}%"
        tva_by_rate[rate_key] = tva_by_rate.get(rate_key, Decimal("0.00")) + line_tva

        line_details.append({
            "label": label,
            "quantity": float(qty),
            "unit_price": float(unit_price),
            "gross_ht": float(gross_line_ht),
            "discount_pct": float(disc_pct),
            "discount_amount": float(line_disc),
            "net_ht": float(net_line_ht),
            "tva_rate_pct": float(tva_pct),
            "tva_amount": float(line_tva),
            "total_ttc": float(line_ttc)
        })

    net_total_ht = total_ht - total_discount
    total_ttc = net_total_ht + total_tva

    formula = f"Total_HT_Brut = {total_ht}; Remise_Totale = {total_discount}; Net_HT = {net_total_ht}; TVA = {total_tva}; TTC = {total_ttc}"

    return {
        "operation": "compound_invoice",
        "inputs": {"items_count": len(items), "currency": currency},
        "formula": formula,
        "result": float(total_ttc),
        "currency_or_unit": currency,
        "is_valid": True,
        "details": {
            "gross_ht": float(total_ht),
            "total_discount": float(total_discount),
            "net_ht": float(net_total_ht),
            "total_tva": float(total_tva),
            "tva_breakdown": {k: float(v) for k, v in tva_by_rate.items()},
            "total_ttc": float(total_ttc),
            "lines": line_details
        }
    }

def compute_statistical_summary(numbers: List[Any], unit: str = "") -> Dict[str, Any]:
    """
    Computes statistical sum, mean, min, max, and median on a series of numbers.
    """
    if not numbers:
        raise ValueError("La liste de nombres ne peut pas être vide.")

    dec_nums = [to_decimal(n) for n in numbers]
    count = len(dec_nums)
    total_sum = sum(dec_nums)
    mean_val = (total_sum / Decimal(count)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    min_val = min(dec_nums)
    max_val = max(dec_nums)

    sorted_nums = sorted(dec_nums)
    if count % 2 == 1:
        median_val = sorted_nums[count // 2]
    else:
        median_val = ((sorted_nums[count // 2 - 1] + sorted_nums[count // 2]) / Decimal(2)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    formula = f"Somme = {total_sum}; Moyenne = {total_sum}/{count} = {mean_val}; Min = {min_val}; Max = {max_val}"

    return {
        "operation": "statistical_summary",
        "inputs": {"count": count, "numbers": [float(n) for n in dec_nums]},
        "formula": formula,
        "result": float(total_sum),
        "currency_or_unit": unit or "unités",
        "is_valid": True,
        "details": {
            "count": count,
            "sum": float(total_sum),
            "mean": float(mean_val),
            "median": float(median_val),
            "min": float(min_val),
            "max": float(max_val)
        }
    }

