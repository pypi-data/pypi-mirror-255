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
    """Переносит все записи из таблицы БД в ее разделы.

    Если до включения партиционирования таблицы БД в ней находились записи, то
    с помощью данной команды их можно перенести в соответствующие разделы.
    Подробнее см. в `educommon.django.db.partitioning.split_table`.

    """
    help = (
        'Command moves all the records from database table to partitions of '
        'this table.'
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
            help='Field name. It will be the partition key.',
        )
        parser.add_argument(
            '--timeout', action='store', dest='timeout',
            default=.0, type=float,
            help=('Timeout (in seconds) between the data transfer iterations. '
                  'It used to reduce the database load.')
        )

    def handle(self, *args, **options):
        app_label = options['app_label']
        model_name = options['model_name']
        field_name = options['field_name']
        timeout = options['timeout']

        try:
            model = get_model(app_label, model_name)
        except LookupError as e:
            raise CommandError(e.message)

        try:
            model._meta.get_field(field_name)
        except FieldDoesNotExist:
            raise CommandError('Invalid field name ({0})'.format(field_name))

        partitioning.split_table(model, field_name, timeout)
