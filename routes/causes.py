from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from models.member import Member
from models.financial import Cause, Contribution
from forms.financial import CauseForm, ContributionForm
from app import db
from utils.decorators import permission_required, log_action
from utils.pdf import generate_contributions_report_pdf
from sqlalchemy import func

causes_bp = Blueprint('causes', __name__, url_prefix='/causes')

@causes_bp.route('/')
@login_required
@permission_required('read')
def index():
    causes = Cause.query.all()
    cause_data = []
    for cause in causes:
        collected = db.session.query(func.sum(Contribution.amount)).filter_by(cause_id=cause.id).scalar() or 0
        percentage = (float(collected) / float(cause.target_amount) * 100) if cause.target_amount > 0 else 0
        cause_data.append({
            'cause': cause,
            'collected': collected,
            'percentage': min(percentage, 100),
            'remaining': max(float(cause.target_amount) - float(collected), 0)
        })
    return render_template('causes/index.html', causes=cause_data)

@causes_bp.route('/add', methods=['GET', 'POST'])
@login_required
@permission_required('write')
def add():
    form = CauseForm()
    if form.validate_on_submit():
        cause = Cause(
            name=form.name.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            target_amount=form.target_amount.data,
            status=form.status.data
        )
        db.session.add(cause)
        db.session.commit()
        log_action(f'Création cause: {cause.name}')
        flash('Cause créée avec succès', 'success')
        return redirect(url_for('causes.index'))
    return render_template('causes/form.html', title='Créer une cause', form=form)

@causes_bp.route('/contribute', methods=['GET', 'POST'])
@login_required
@permission_required('write')
def contribute():
    form = ContributionForm()
    form.cause_id.choices = [(c.id, c.name) for c in Cause.query.filter_by(status='Active').all()]
    form.member_id.choices = [(m.id, m.full_name) for m in Member.query.filter_by(active=True).all()]
    if form.validate_on_submit():
        contribution = Contribution(
            cause_id=form.cause_id.data,
            member_id=form.member_id.data,
            amount=form.amount.data,
            date_paid=form.date_paid.data,
            notes=form.notes.data,
            created_by=current_user.id
        )
        db.session.add(contribution)
        db.session.commit()
        log_action(f'Contribution à la cause {contribution.cause.name}: {contribution.member.full_name}')
        flash('Contribution enregistrée avec succès', 'success')
        return redirect(url_for('causes.index'))
    return render_template('causes/contribute.html', title='Enregistrer une contribution', form=form)

@causes_bp.route('/view/<int:id>')
@login_required
@permission_required('read')
def view(id):
    cause = Cause.query.get_or_404(id)
    contributions = Contribution.query.filter_by(cause_id=id).order_by(Contribution.date_paid.desc()).all()
    total_collected = db.session.query(func.sum(Contribution.amount)).filter_by(cause_id=id).scalar() or 0
    return render_template('causes/view.html', cause=cause, contributions=contributions, total_collected=total_collected)

@causes_bp.route('/export_pdf/<int:id>')
@login_required
@permission_required('read')
def export_pdf(id):
    cause = Cause.query.get_or_404(id)
    contributions = Contribution.query.filter_by(cause_id=id).order_by(Contribution.date_paid.desc()).all()
    total_collected = db.session.query(func.sum(Contribution.amount)).filter_by(cause_id=id).scalar() or 0
    pdf_buffer = generate_contributions_report_pdf(cause.name, contributions, total_collected)
    log_action(f'Export PDF contributions cause: {cause.name}')
    return send_file(pdf_buffer, download_name=f'Rapport_Contributions_{cause.name}.pdf', mimetype='application/pdf')
