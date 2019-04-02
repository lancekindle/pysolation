from django.urls import path

from . import views

app_name = 'django_pysolation'  # give an official namespace
urlpatterns = [
    path('', views.index),
]