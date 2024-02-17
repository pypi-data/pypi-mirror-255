from objectpack.actions import (
    ObjectPack,
)

from educommon.contingent.contingent_plugin.models import (
    ContingentModelChanged,
)


class ContingentModelChangedPack(ObjectPack):

    title = 'Измененные объекты контингента'
    model = ContingentModelChanged

    columns = [
        {
            'data_index': 'content_type',
            'header': 'Тип'
        },
        {
            'data_index': 'content_object',
            'header': 'Объект'
        }
    ]

    def extend_menu(self, menu):
        return menu.SubMenu(
            'Администрирование', menu.Item(
                self.title, self.list_window_action
            )
        )
