from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.member import Member
from app.models.financial import Cotisation
from app.forms.financial import CotisationForm
from app import db
from app.utils.decorators import permission_required, log_action
from datetime import datetime

cotisations_bp = Blueprint('cotisations', __name__, url_prefix='/cotisations')

@cotisations_bp.route('/')
@login_required
@permission_required('read')
def index():
    cotisations = Cotisation.query.order_by(Cotisation.date_paid.desc()).all()
    return render_template('cotisations/index.html', cotisations=cotisations)

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
