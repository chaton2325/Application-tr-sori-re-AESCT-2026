from flask import Blueprint, render_template, send_file, request
from flask_login import login_required
from app.models.financial import FinanceEntry, Cotisation, Contribution
from app.utils.decorators import permission_required
import io
# Using openpyxl directly to avoid pandas dependency if not strictly needed for simple exports
from openpyxl import Workbook

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
@permission_required('read')
def index():
    return render_template('reports/index.html')

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
