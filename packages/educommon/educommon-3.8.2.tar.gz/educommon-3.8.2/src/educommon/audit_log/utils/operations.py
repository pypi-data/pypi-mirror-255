# pylint: disable=abstract-method
import codecs
import os

from django.conf import (
    settings,
)
from django.db.migrations.operations.base import (
    Operation,
)

from educommon.audit_log.constants import (
    PG_LOCK_ID,
    SQL_FILES_DIR,
)
from educommon.audit_log.utils import (
    get_db_connection_params,
)


class ReinstallAuditLog(Operation):
    """Пересоздаёт функции журнала изменений в БД.

    Используется для миграции после модификации sql файла.

    Удаляет схему audit. В этой схеме не должно храниться никаких таблиц
    с данными.
    После удаления устанавливает audit_log заново.
    """

    reversible = True

    @staticmethod
    def _read_sql(filename):
        sql_file_path = os.path.join(SQL_FILES_DIR, filename)
        with codecs.open(sql_file_path, 'r', 'utf-8') as sql_file:
            sql = sql_file.read().replace('%', '%%')
        return sql

    @property
    def _install_sql(self):
        params = get_db_connection_params()
        params['lock_id'] = PG_LOCK_ID
        return self._read_sql('install_audit_log.sql').format(**params)

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state,
                          to_state):
        if schema_editor.connection.alias == settings.DEFAULT_DB_ALIAS:
            schema_editor.execute(self._install_sql)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        return None
