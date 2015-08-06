from django.conf.urls import url, patterns, include
from . import views
from django.views.generic import ListView, DetailView
from autopatch.models import Server
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    url(r'^$', views.Home ),
    url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^prod/$', views.ProdView),
    url(r'^stage/$', views.StageView),
    url(r'^qa/$', views.QAView),
    url(r'^dev/$', views.DevView),
    url(r'^home/$', views.Home, name='Home'),
    url(r'create/$', views.create),
    url(r'genlist/$', views.GetList),
    url(r'hostlist/$', views.AllHosts.as_view()),
    url(r'^tasks/', views.TasksView.as_view()),
    url(r'^csv/', views.CreateCSV),
    url(r'^git/', views.Git),
    url(r'^devsat/', views.DevSat),
]
