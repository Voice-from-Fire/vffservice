from app.service import app
from app.ops.user import remove_user, get_user_by_name

from app.db.models import AuditLog, EventType

import pytest

from app.ops.audit_log import add_audit_log

def test_add_audit_log(db_session):
    add_audit_log(db=db_session, commit=True, event=EventType.user_new, user=15)
    assert db_session.query(AuditLog).filter(AuditLog.user == 15).count() == 1
    add_audit_log(db=db_session, commit=False, event=EventType.user_new, user=15)
    assert db_session.query(AuditLog).filter(AuditLog.user == 15).count() == 1
    add_audit_log(db=db_session, commit=True, event=EventType.user_deleted, user=15)
    assert db_session.query(AuditLog).filter(AuditLog.user == 15).count() == 3
