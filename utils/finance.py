from sqlalchemy import func
from app import db
from models.financial import FinanceEntry, Cotisation, Contribution


def get_overall_balance():
    """Solde général actuel de la trésorerie (toutes opérations confondues, à ce jour)."""
    total_incomes = db.session.query(func.sum(FinanceEntry.amount)).filter_by(type='Income').scalar() or 0
    total_expenses = db.session.query(func.sum(FinanceEntry.amount)).filter_by(type='Expense').scalar() or 0
    cotisations_total = db.session.query(func.sum(Cotisation.amount_paid)).scalar() or 0
    contributions_total = db.session.query(func.sum(Contribution.amount)).scalar() or 0
    return (float(total_incomes) + float(cotisations_total) + float(contributions_total)) - float(total_expenses)


def get_cause_balance(cause_id, contributions_total=None):
    """Bilan financier d'une cause : contributions + encaissements liés - décaissements liés.

    Un solde négatif signifie que les décaissements rattachés à la cause dépassent les sommes
    qui lui ont été collectées : le manque est alors financé par le solde général de la trésorerie.
    """
    if contributions_total is None:
        contributions_total = db.session.query(func.sum(Contribution.amount)).filter_by(cause_id=cause_id).scalar() or 0
    income_linked = db.session.query(func.sum(FinanceEntry.amount)).filter_by(cause_id=cause_id, type='Income').scalar() or 0
    expense_linked = db.session.query(func.sum(FinanceEntry.amount)).filter_by(cause_id=cause_id, type='Expense').scalar() or 0
    contributions_total = float(contributions_total)
    income_linked = float(income_linked)
    expense_linked = float(expense_linked)
    return {
        'contributions': contributions_total,
        'income_linked': income_linked,
        'expense_linked': expense_linked,
        'balance': contributions_total + income_linked - expense_linked,
    }
