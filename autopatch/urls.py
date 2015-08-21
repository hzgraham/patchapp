#importing built-in Django libraries
from django.conf.urls import url, patterns, include
from django.views.generic import ListView, DetailView
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

#importing autopatch app specific libraries
from . import views
#from autopatch.models import Server

urlpatterns = [
    #main templates for framework and home page
    url(r'^$', views.Home ),
    url(r'^home/$', views.Home, name='Home'),

    #This uses a view that returns the results.html view for a host
    url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),

    #Patching Tasks
    url(r'^tasks/', views.TasksView.as_view()),
    #where the errata levels are set manually
    url(r'^errata/$', views.UpdateErrata),
    #Where excluded owners are set
    url(r'^owners/$', views.SetOwners),
    #Creates the .csv files
    url(r'^csv/', views.CreateCSV),
    #Clones a git repo and imports server info
    url(r'^git/', views.Git),

    #Satellite links
    url(r'^satid/', views.SatId),
    url(r'^satupdates/', views.SatUpdates),

    #List views of hosts for the different environments
    url(r'^prod/$', views.ProdView),
    url(r'^stage/$', views.StageView),
    url(r'^qa/$', views.QAView),
    url(r'^dev/$', views.DevView),
]
