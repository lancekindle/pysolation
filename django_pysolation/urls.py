from django.urls import path, re_path

from . import views

app_name = 'django_pysolation'  # give an official namespace
urlpatterns = [
    path('', views.index),
    re_path(r'^(?P<uuid>[0-9a-zA-Z]+)$', views.index),
    re_path(r'^(?P<uuid>[0-9a-zA-Z]+)/$', views.index),
    re_path(r'^(?P<uuid>[0-9a-zA-Z]+)/refresh/(?P<timestamp>[0-9a-zA-Z]+)$', views.refresh),
    re_path(r'^(?P<uuid>[0-9a-zA-Z]+)/move_player_to/(?P<x>[0-9]+),(?P<y>[0-9]+)$', views.move_player_to),
    re_path(r'^(?P<uuid>[0-9a-zA-Z]+)/remove_tile_at/(?P<x>[0-9]+),(?P<y>[0-9]+)$', views.remove_tile_at),
]