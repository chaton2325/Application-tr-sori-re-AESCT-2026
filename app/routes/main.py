from flask import Blueprint, render_template
from flask_login import login_required
from app.models.member import Member
from app.models.financial import Cause, Cotisation, FinanceEntry, Contribution
from sqlalchemy import func
from app import db
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    member_count = Member.query.filter_by(active=True).count()
    active_causes_count = Cause.query.filter_by(status='Active').count()
    
    # Financial summaries
    total_incomes = db.session.query(func.sum(FinanceEntry.amount)).filter_by(type='Income').scalar() or 0
    total_expenses = db.session.query(func.sum(FinanceEntry.amount)).filter_by(type='Expense').scalar() or 0
    
    cotisations_total = db.session.query(func.sum(Cotisation.amount_paid)).scalar() or 0
    contributions_total = db.session.query(func.sum(Contribution.amount)).scalar() or 0
    
    overall_balance = (float(total_incomes) + float(cotisations_total) + float(contributions_total)) - float(total_expenses)
    
    # Chart data aggregation (last 6 months)
    chart_labels = []
    income_data = []
    expense_data = []
    
    for i in range(5, -1, -1):
        month_date = datetime.now() - timedelta(days=30*i)
        month = month_date.month
        year = month_date.year
        chart_labels.append(month_date.strftime('%b'))
        
        # Incomes
        inc = (db.session.query(func.sum(FinanceEntry.amount)).filter(FinanceEntry.type=='Income', func.extract('month', FinanceEntry.date)==month, func.extract('year', FinanceEntry.date)==year).scalar() or 0)
        cot = (db.session.query(func.sum(Cotisation.amount_paid)).filter(Cotisation.month==month, Cotisation.year==year).scalar() or 0)
        con = (db.session.query(func.sum(Contribution.amount)).filter(func.extract('month', Contribution.date_paid)==month, func.extract('year', Contribution.date_paid)==year).scalar() or 0)
        income_data.append(float(inc) + float(cot) + float(con))
        
        # Expenses
        exp = (db.session.query(func.sum(FinanceEntry.amount)).filter(FinanceEntry.type=='Expense', func.extract('month', FinanceEntry.date)==month, func.extract('year', FinanceEntry.date)==year).scalar() or 0)
        expense_data.append(float(exp))
    
    return render_template('main/index.html', 
                           member_count=member_count,
                           active_causes_count=active_causes_count,
                           overall_balance=overall_balance,
                           total_incomes=float(total_incomes) + float(cotisations_total) + float(contributions_total),
                           total_expenses=float(total_expenses),
                           chart_labels=chart_labels,
                           income_data=income_data,
                           expense_data=expense_data)
