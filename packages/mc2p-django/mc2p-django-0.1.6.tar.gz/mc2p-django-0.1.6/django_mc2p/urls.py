from django.urls import re_path

from . import views


urlpatterns = [
    re_path(r'^notify/$', views.MC2PNotifyView.as_view(), name='mc2p-notify'),
]
