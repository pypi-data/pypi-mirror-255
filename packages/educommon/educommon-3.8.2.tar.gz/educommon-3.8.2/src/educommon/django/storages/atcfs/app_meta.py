from django.conf.urls import (
    url,
)
from django.views.generic import (
    TemplateView,
)


def register_urlpatterns():
    urlpatterns = [
        url(
            r'^atcfs_unavailable/$',
            TemplateView.as_view(template_name='atcfs_unavailable.html'),
            name='atcfs_unavailable'
        ),
    ]

    return urlpatterns
