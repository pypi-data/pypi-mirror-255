from django.apps import (
    AppConfig as AppConfigBase,
)


class AppConfig(AppConfigBase):

    name = __package__
    label = 'async_task'
