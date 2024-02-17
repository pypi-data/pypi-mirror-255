from django.core.management.base import (
    CommandError,
)
from django.db.models.fields import (
    FieldDoesNotExist,
)
from m3_django_compat import (
    BaseCommand,
    get_model,
)

from educommon.django.db import (
    partitioning,
)


class Command(BaseCommand):
    """Удаляет записи из таблицы БД по условию.

    С помощью данной команды удаляются записи из основной (не секционированной)
    таблицы, у которых значение в field_name меньше значения из before_value.
    Подробнее см. в `educommon.django.db.partitioning.clear_table`.

    """
    help = (
        'Command deletes all the records from database table when '
        'field_name < before_value.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'app_label',
            help='App label of an application.',
        )
        parser.add_argument(
            'model_name',
            help='Model name.',
        )
        parser.add_argument(
            'field_name',
            help='Field name. It will be a check column.',
        )
        parser.add_argument(
            'before_value',
            help='Deleting rows before this value.',
        )
        parser.add_argument(
            '--timeout', action='store', dest='timeout',
            default=.0, type=float,
            help=('Timeout (in seconds) between the data removes iterations. '
                  'It used to reduce the database load.')
        )

    def handle(self, *args, **options):
        app_label = options['app_label']
        model_name = options['model_name']
        field_name = options['field_name']
        before_value = options['before_value']
        timeout = options['timeout']

        try:
            model = get_model(app_label, model_name)
        except LookupError as e:
            raise CommandError(e.message)

        try:
            model._meta.get_field(field_name)
        except FieldDoesNotExist:
            raise CommandError('Invalid field name ({0})'.format(field_name))

        partitioning.clear_table(model, field_name, before_value, timeout)
