from django.urls import re_path, include 
from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='index')
]