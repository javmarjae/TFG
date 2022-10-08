from django.conf import settings
from django.urls import re_path, include, path 
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    re_path(r'^$', views.index, name='index')
]

urlpatterns += [
    path('profile/<username>', views.profile, name='profile'),
    path('clans', views.clans, name='clans'),
    path('clan/<name>', views.clanprofile, name='clan'),
]

for module in settings.MODULES:
    urlpatterns += [
        path('{}/'.format(module), include('{}.urls'.format(module)))
    ]