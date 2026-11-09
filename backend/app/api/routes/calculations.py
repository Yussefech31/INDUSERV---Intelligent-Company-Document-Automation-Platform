import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.entities import CalculationAudit
from app.schemas.schemas import CalculationRequest, CalculationAuditResponse
from app.services.calculations import financial_math

router = APIRouter(prefix="/calculations", tags=["Calculations"])

@router.post("/compute", response_model=CalculationAuditResponse)
def compute_calculation(req: CalculationRequest, db: Session = Depends(get_db)):
    """
    Execute deterministic financial or mathematical computation using Python Decimal.
    Returns input values, exact formula, result, currency/unit, and validation audit.
    """
    try:
        if req.operation == "ht_to_ttc":
            if req.ht_amount is None:
                raise HTTPException(status_code=400, detail="Le montant 'ht_amount' est obligatoire pour ce calcul.")
            calc_data = financial_math.compute_ht_to_ttc(
                ht_amount=req.ht_amount,
                tva_rate=req.tva_rate or 20.0,
                discount_rate=req.discount_rate or 0.0,
                currency=req.currency or "EUR"
            )

        elif req.operation in ["margin", "margin_and_markup"]:
            if req.cost_price is None or req.selling_price is None:
                raise HTTPException(status_code=400, detail="'cost_price' et 'selling_price' sont obligatoires.")
            calc_data = financial_math.compute_margin_and_markup(
                cost_price=req.cost_price,
                selling_price=req.selling_price,
                currency=req.currency or "EUR"
            )

        elif req.operation == "budget_variance":
            if req.budget_planned is None or req.budget_actual is None:
                raise HTTPException(status_code=400, detail="'budget_planned' et 'budget_actual' sont obligatoires.")
            calc_data = financial_math.compute_budget_variance(
                budget_planned=req.budget_planned,
                budget_actual=req.budget_actual,
                currency=req.currency or "EUR"
            )

        elif req.operation in ["compound_invoice", "vat_summary"]:
            if not req.items:
                raise HTTPException(status_code=400, detail="Une liste d'articles 'items' est requise.")
            calc_data = financial_math.compute_compound_invoice(
                items=[i.model_dump() for i in req.items],
                currency=req.currency or "EUR"
            )

        elif req.operation in ["sum", "statistical_summary"]:
            if not req.numbers:
                raise HTTPException(status_code=400, detail="Une liste de nombres 'numbers' est requise.")
            calc_data = financial_math.compute_statistical_summary(
                numbers=req.numbers,
                unit=req.currency
            )

        else:
            raise HTTPException(status_code=400, detail=f"Opération de calcul inconnue: {req.operation}")

        # Save audit record
        audit = CalculationAudit(
            operation=calc_data["operation"],
            inputs_json=json.dumps(calc_data["inputs"], ensure_ascii=False),
            formula=calc_data["formula"],
            result=str(calc_data["result"]),
            currency_or_unit=calc_data["currency_or_unit"],
            is_valid=calc_data["is_valid"]
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)

        return CalculationAuditResponse(
            id=audit.id,
            operation=calc_data["operation"],
            inputs=calc_data["inputs"],
            formula=calc_data["formula"],
            result=calc_data["result"],
            currency_or_unit=calc_data["currency_or_unit"],
            is_valid=calc_data["is_valid"],
            details=calc_data.get("details")
        )

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de calcul: {str(e)}")

@router.get("/audits", response_model=List[CalculationAuditResponse])
def list_calculation_audits(db: Session = Depends(get_db)):
    """Retrieve historical deterministic calculation audits."""
    audits = db.query(CalculationAudit).order_by(CalculationAudit.created_at.desc()).limit(50).all()
    results = []
    for a in audits:
        inputs = {}
        try:
            inputs = json.loads(a.inputs_json or "{}")
        except Exception:
            pass
        results.append(CalculationAuditResponse(
            id=a.id,
            operation=a.operation,
            inputs=inputs,
            formula=a.formula,
            result=float(a.result) if a.result.replace(".", "", 1).isdigit() else a.result,
            currency_or_unit=a.currency_or_unit,
            is_valid=a.is_valid
        ))
    return results

