from sqlalchemy.orm import Session
from ..db.models import AuditLog


def add_audit_log(db: Session, commit=False, **kwargs):
    audit_log = AuditLog(**kwargs)
    db.add(audit_log)
    if commit:
        db.commit()
