from django.urls import path, re_path

from . import views

app_name = 'django_pysolation'  # give an official namespace
urlpatterns = [
    path('', views.index),
    path('move_player_to', views.move_player_to),
    re_path(r'^move_player_to/(?P<x>[0-9]+),(?P<y>[0-9]+)$', views.move_player_to),
]