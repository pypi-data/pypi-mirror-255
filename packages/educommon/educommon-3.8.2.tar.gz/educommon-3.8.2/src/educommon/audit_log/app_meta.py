from educommon import (
    ioc,
)
from educommon.audit_log.actions import (
    AuditLogPack,
)
from educommon.audit_log.error_log.actions import (
    PostgreSQLErrorPack,
)


def register_actions():
    ioc.get('main_controller').packs.extend((
        AuditLogPack(),
        PostgreSQLErrorPack(),
    ))
