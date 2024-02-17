from django.db import (
    router,
)
from m3_django_compat import (
    BaseCommand,
    get_model,
)

from educommon.django.db import (
    partitioning,
)


class Command(BaseCommand):
    """Применяет партицирование к таблице переданной модели.

    Команда, если это необходимо, сперва инициализирует средства партицирования
    для БД, в которой хранится переданная модель, а затем создает необходимые
    триггеры. Подробнее см. в `educommon.django.db.partitioning.init` и
    `educommon.django.db.partitioning.set_partitioning_for_model`.

    """
    help = 'Applies partitioning to the table.'

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

    def handle(self, *args, **options):
        app_label = options['app_label']
        model_name = options['model_name']
        field_name = options['field_name']
        Model = get_model(app_label, model_name)
        db_alias = router.db_for_write(Model)

        if not partitioning.is_initialized(db_alias):
            partitioning.init(db_alias)

        partitioning.set_partitioning_for_model(Model, field_name, force=True)
