===============================
Инструкции по обновлению пакета
===============================

***************
0.14.x → 0.15.x
***************

1. В версии 0.15.0 выполнен рефакторинг класса ``ContingentFieldsObserver`` (модуль ``educommon.contingent.contingent_plugin.observer``). После рефакторинга словарь с наблюдаемыми полями нобходимо передавать в конструктор класса (ранее предполагалось использование потомков класса), соответственно больше нет необходимости создавать свой класс наблюдателя. Также после рефакторинга нет необходимости включать наблюдение за каждой из моделей - наблюдение будет работать автоматически.

  Если ранее создание наблюдателя выглядело примерно так:

  ::

    from educommon.contingent.contingent_plugin import observer

    class ContingentFieldObserver(observer.ContingentFieldsObserver):
        model_fields = {
            ('person', 'Person'): (
                'firstname',
                'patronymic',
                'surname',
            ),
        }

    observer = ContingentFieldObserver()
    for app_label, model in observer.model_fields.keys():
        observer.observe(apps.get_model(app_label, model))

  то после рефакторинга наблюдатель следует создавать так:

  ::

    from educommon.contingent.contingent_plugin.observer import ContingentFieldsObserver

    model_fields = {
        ('person', 'Person'): (
            'firstname',
            'patronymic',
            'surname',
        ),
    }
    observer = ContingentFieldObserver(model_fields)
