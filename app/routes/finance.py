import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models.financial import FinanceEntry, Category
from app.forms.financial import FinanceEntryForm
from app import db
from app.utils.decorators import permission_required, log_action
from werkzeug.utils import secure_filename
from datetime import datetime

finance_bp = Blueprint('finance', __name__, url_prefix='/finance')

@finance_bp.route('/')
@login_required
@permission_required('read')
def index():
    entries = FinanceEntry.query.order_by(FinanceEntry.date.desc()).all()
    return render_template('finance/index.html', entries=entries)

@finance_bp.route('/add', methods=['GET', 'POST'])
@login_required
@permission_required('write')
def add():
    form = FinanceEntryForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    if form.validate_on_submit():
        filename = None
        if form.attachment.data:
            f = form.attachment.data
            filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{f.filename}")
            f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        
        # Generate automatic reference
        count = FinanceEntry.query.count() + 1
        ref = f"OP-{datetime.now().year}-{count:05d}"
        
        entry = FinanceEntry(
            ref=ref,
            type=form.type.data,
            category_id=form.category_id.data,
            amount=form.amount.data,
            date=form.date.data,
            label=form.label.data,
            attachment_path=filename,
            created_by=current_user.id
        )
        db.session.add(entry)
        db.session.commit()
        log_action(f'Opération financière {ref}: {entry.label}')
        flash('Opération enregistrée avec succès', 'success')
        return redirect(url_for('finance.index'))
    return render_template('finance/form.html', title='Nouvelle opération', form=form)
