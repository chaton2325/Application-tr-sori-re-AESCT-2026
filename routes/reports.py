from flask import Blueprint, render_template, send_file, request
from flask_login import login_required
from models.financial import FinanceEntry, Cotisation, Contribution
from utils.decorators import permission_required, log_action
from utils.pdf import generate_monthly_bilan_pdf
from utils.finance import get_overall_balance
from datetime import datetime
from sqlalchemy import extract
import io
# Using openpyxl directly to avoid pandas dependency if not strictly needed for simple exports
from openpyxl import Workbook

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
@permission_required('read')
def index():
    return render_template('reports/index.html', now_year=datetime.now().year, now_month=datetime.now().month)

@reports_bp.route('/export/excel')
@login_required
@permission_required('read')
def export_excel():
    entries = FinanceEntry.query.all()
    wb = Workbook()
    ws = wb.active
    ws.title = "Finances"
    
    headers = ['Date', 'Référence', 'Libellé', 'Catégorie', 'Type', 'Montant']
    ws.append(headers)
    
    for e in entries:
        ws.append([e.date.strftime('%d/%m/%Y'), e.ref, e.label, e.category.name, e.type, float(e.amount)])
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='rapport_finances.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@reports_bp.route('/export/bilan-mensuel', methods=['POST'])
@login_required
@permission_required('read')
def export_monthly_bilan():
    month = int(request.form.get('month'))
    year = int(request.form.get('year'))

    income_entries = FinanceEntry.query.filter(
        FinanceEntry.type == 'Income',
        extract('month', FinanceEntry.date) == month,
        extract('year', FinanceEntry.date) == year
    ).order_by(FinanceEntry.date.asc()).all()

    expense_entries = FinanceEntry.query.filter(
        FinanceEntry.type == 'Expense',
        extract('month', FinanceEntry.date) == month,
        extract('year', FinanceEntry.date) == year
    ).order_by(FinanceEntry.date.asc()).all()

    cotisations = Cotisation.query.filter_by(month=month, year=year).order_by(Cotisation.date_paid.asc()).all()

    contributions = Contribution.query.filter(
        extract('month', Contribution.date_paid) == month,
        extract('year', Contribution.date_paid) == year
    ).order_by(Contribution.date_paid.asc()).all()

    overall_balance = get_overall_balance()
    pdf_buffer = generate_monthly_bilan_pdf(
        month, year, income_entries, expense_entries, cotisations, contributions,
        overall_balance=overall_balance
    )
    log_action(f'Export PDF Bilan Mensuel Global: {month}/{year}')
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f'Bilan_Mensuel_AESCT_{month:02d}_{year}.pdf',
        mimetype='application/pdf'
    )
