#from django.urls import path, re_path  #django 2.0+
from django.conf.urls import url

from . import views

app_name = 'django_pysolation'  # give an official namespace
urlpatterns = [
    url(r'^$', views.index),
    url(r'^join/(?P<uuid>[0-9a-zA-Z]+)/$', views.join, name='join-game'),
    url(r'^join$', views.join),
    url(r'^(?P<uuid>[0-9a-zA-Z]+)$', views.index, name='game-page'),
    url(r'^(?P<uuid>[0-9a-zA-Z]+)/$', views.index),
    url(r'^(?P<uuid>[0-9a-zA-Z]+)/refresh/(?P<timestamp>[0-9a-zA-Z]+)$', views.refresh),
    url(r'^(?P<uuid>[0-9a-zA-Z]+)/move_player_to/(?P<x>[0-9]+),(?P<y>[0-9]+)$', views.move_player_to),
    url(r'^(?P<uuid>[0-9a-zA-Z]+)/remove_tile_at/(?P<x>[0-9]+),(?P<y>[0-9]+)$', views.remove_tile_at),
]