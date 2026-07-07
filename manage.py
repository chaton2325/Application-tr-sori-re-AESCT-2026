from app import create_app, db
from app.models.user import User, Role
from app.models.member import Member
from app.models.financial import Cotisation, Cause, Contribution, FinanceEntry, Category
from app.models.audit import AuditLog

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Role': Role, 
        'Member': Member,
        'Cotisation': Cotisation,
        'Cause': Cause,
        'Contribution': Contribution,
        'FinanceEntry': FinanceEntry,
        'Category': Category,
        'AuditLog': AuditLog
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0')
