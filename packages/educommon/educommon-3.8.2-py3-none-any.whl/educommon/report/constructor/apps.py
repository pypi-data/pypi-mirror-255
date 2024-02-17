from django.apps import (
    config,
)
from django.db.models import (
    CharField,
    TextField,
)
from django.db.models.functions import (
    Lower,
)


class AppConfig(config.AppConfig):

    name = __name__.rpartition('.')[0]
    label = 'report_constructor'

    def ready(self):
        CharField.register_lookup(Lower)
        TextField.register_lookup(Lower)
