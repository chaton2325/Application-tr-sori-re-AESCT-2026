from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from models.member import Member
from forms.members import MemberForm
from app import db
from utils.decorators import permission_required, log_action

members_bp = Blueprint('members', __name__, url_prefix='/members')

@members_bp.route('/')
@login_required
@permission_required('read')
def index():
    members = Member.query.all()
    return render_template('members/index.html', members=members)

@members_bp.route('/add', methods=['GET', 'POST'])
@login_required
@permission_required('write')
def add():
    form = MemberForm()
    if form.validate_on_submit():
        member = Member(
            last_name=form.last_name.data,
            first_name=form.first_name.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data,
            join_date=form.join_date.data,
            active=form.active.data
        )
        db.session.add(member)
        db.session.commit()
        log_action(f'Ajout adhérent: {member.full_name}')
        flash('Adhérent ajouté avec succès', 'success')
        return redirect(url_for('members.index'))
    return render_template('members/form.html', title='Ajouter un adhérent', form=form)

@members_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required('write')
def edit(id):
    member = Member.query.get_or_404(id)
    form = MemberForm(obj=member)
    if form.validate_on_submit():
        form.populate_obj(member)
        db.session.commit()
        log_action(f'Modification adhérent: {member.full_name}')
        flash('Adhérent modifié avec succès', 'success')
        return redirect(url_for('members.index'))
    return render_template('members/form.html', title='Modifier un adhérent', form=form)

@members_bp.route('/view/<int:id>')
@login_required
@permission_required('read')
def view(id):
    member = Member.query.get_or_404(id)
    return render_template('members/view.html', member=member)
