from app import create_app, db
from models.user import User, Role
from models.member import Member
from models.financial import Cotisation, Cause, Contribution, FinanceEntry, Category
from models.audit import AuditLog

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
    app.run(host='0.0.0.0' , port=8083)
