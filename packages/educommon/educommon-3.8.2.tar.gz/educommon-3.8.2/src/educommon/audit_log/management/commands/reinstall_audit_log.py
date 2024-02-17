import codecs
import os

from django.core.management.base import (
    BaseCommand,
)
from django.db import (
    connection,
)

from educommon.audit_log.constants import (
    INSTALL_AUDIT_LOG_SQL_FILE_NAME,
    PG_LOCK_ID,
    SQL_FILES_DIR,
)
from educommon.audit_log.utils import (
    clear_audit_logs,
    configure,
    get_db_connection_params,
)


DEFAULT_QUERYSET_CHUNK_SIZE = 1_000


class Command(BaseCommand):
    """Пересоздаёт функции журнала изменений в БД.

    Используется для миграции после модификации sql файла.

    Удаляет схему audit. В этой схеме не должно храниться никаких таблиц
    с данными.
    После удаления устанавливает audit_log заново.
    """

    help = 'Команда для переустановки audit_log.'

    def add_arguments(self, parser):
        """Добавление аргументов команды."""
        parser.add_argument(
            '--clear_audit_logs',
            action='store_true',
            default=False,
            help='Удалить записи из audit_log для неотслеживаемых таблиц',
        ),
        parser.add_argument(
            '--chunk_size', type=int, default=DEFAULT_QUERYSET_CHUNK_SIZE,
            help='Кол-во единовременно удаляемых записей',
        )

    def _read_sql(self, filename):
        """Чтение SQL-кода из файла."""
        sql_file_path = os.path.join(SQL_FILES_DIR, filename)

        with codecs.open(sql_file_path, 'r', 'utf-8') as sql_file:
            sql = sql_file.read()

        self.stdout.write('reading SQL-code..\n')

        return sql

    def _prepare_sql(self):
        """Подготовка SQL-кода."""
        params = get_db_connection_params()
        params['lock_id'] = PG_LOCK_ID

        self.stdout.write('preparing SQL-code..\n')

        return self._read_sql(INSTALL_AUDIT_LOG_SQL_FILE_NAME).format(**params)

    def handle(self, *args, **options):
        """Формирование SQL-кода и его исполнение."""
        self.stdout.write('start reinstalling audit_log..\n')

        cursor = connection.cursor()

        cursor.execute(self._prepare_sql())

        configure(force_update_triggers=True)

        if options['clear_audit_logs']:
            self.stdout.write('clearing audit_log...\n')

            deleted_table_counts = clear_audit_logs(chunk_size=options['chunk_size'])

            if deleted_table_counts:
                self.stdout.write('deleted audit_log records for tables:\n')
                for deleted_table, count in deleted_table_counts.items():
                    self.stdout.write(f'\t{deleted_table}: {count}\n')

        self.stdout.write('reinstalling audit_log finished.\n')
