from django.urls import re_path, include, path 
from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='index')
]

urlpatterns += [
    path('profile/<username>', views.profile, name='profile'),
    path('clans', views.clans, name='clans'),
    path('clan/<name>', views.clanprofile, name='clan'),
    path('friends',views.friends,name='friends'),
    path('chat/', include('chat.urls')),
    path('users/',views.users,name='users'),
    path('authentication', include('authentication.urls')),
    path('report/', views.create_report,name='report'),
    path('reports/', views.reports, name='reports'),
    path('reportdetails/<uuid:report_id>', views.report_details, name='reportdetails')
]
