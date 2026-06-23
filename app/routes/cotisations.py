from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from app.models.member import Member
from app.models.financial import Cotisation
from app.forms.financial import CotisationForm
from app import db
from app.utils.decorators import permission_required, log_action
from app.utils.pdf import generate_cotisations_report_pdf
from datetime import datetime
from sqlalchemy import func, and_

cotisations_bp = Blueprint('cotisations', __name__, url_prefix='/cotisations')

@cotisations_bp.route('/')
@login_required
@permission_required('read')
def index():
    # Properly aggregate data for chart
    monthly_data = db.session.query(
        Cotisation.month,
        Cotisation.year,
        func.sum(Cotisation.amount_paid)
    ).group_by(
        Cotisation.year,
        Cotisation.month
    ).order_by(
        Cotisation.year.desc(),
        Cotisation.month.desc()
    ).limit(12).all()
    
    # Debug print
    print(f"DEBUG: Monthly Data: {monthly_data}")
    
    # Process data: ensure it's sorted by time ascending for the chart
    sorted_data = sorted(monthly_data, key=lambda x: (x[1], x[0]))
    
    chart_labels = [f"{m}/{y}" for m, y, amt in sorted_data]
    chart_values = [float(amt) if amt else 0 for m, y, amt in sorted_data]

    cotisations = Cotisation.query.order_by(Cotisation.date_paid.desc()).all()
    return render_template('cotisations/index.html', cotisations=cotisations, chart_labels=chart_labels, chart_values=chart_values, now_year=datetime.now().year)

@cotisations_bp.route('/add', methods=['GET', 'POST'])
@login_required
@permission_required('write')
def add():
    form = CotisationForm()
    form.member_id.choices = [(m.id, m.full_name) for m in Member.query.filter_by(active=True).all()]
    if form.validate_on_submit():
        cotisation = Cotisation(
            member_id=form.member_id.data,
            month=form.month.data,
            year=form.year.data,
            amount_expected=form.amount_expected.data,
            amount_paid=form.amount_paid.data,
            date_paid=form.date_paid.data,
            notes=form.notes.data,
            created_by=current_user.id
        )
        db.session.add(cotisation)
        db.session.commit()
        log_action(f'Paiement cotisation: {cotisation.member.full_name} - {cotisation.month}/{cotisation.year}')
        flash('Cotisation enregistrée avec succès', 'success')
        return redirect(url_for('cotisations.index'))
    
    if request.method == 'GET':
        form.month.data = datetime.now().month
        form.year.data = datetime.now().year
        form.date_paid.data = datetime.now().date()
        
    return render_template('cotisations/form.html', title='Enregistrer une cotisation', form=form)

@cotisations_bp.route('/export_pdf', methods=['POST'])
@login_required
@permission_required('read')
def export_pdf():
    # Note: Flask-WTF CSRFProtect expects 'csrf_token' field in the form.
    # By using a regular form in HTML, we MUST ensure the token is passed and validated if required globally,
    # or ensure it's not strictly enforced on this specific route if configured.
    # The fix in the template should be sufficient if CSRFProtect is configured.
    
    month = int(request.form.get('month'))
    year = int(request.form.get('year'))
    cotisations = Cotisation.query.filter_by(month=month, year=year).order_by(Cotisation.date_paid.desc()).all()
    total_collected = db.session.query(func.sum(Cotisation.amount_paid)).filter_by(month=month, year=year).scalar() or 0
    
    pdf_buffer = generate_cotisations_report_pdf(month, year, cotisations, total_collected)
    log_action(f'Export PDF cotisations: {month}/{year}')
    return send_file(pdf_buffer, download_name=f'Rapport_Cotisations_{month}_{year}.pdf', mimetype='application/pdf')
