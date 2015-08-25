#importing built-in Django libraries
from django.conf.urls import url, patterns, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# importing autopatch app specific libraries
from . import views

urlpatterns = [
    # main templates for framework and home page
    url(r'^$', views.Home ),
    url(r'^home/$', views.Home, name='Home'),

    # This uses a view that returns the results.html view for a host
    url(r'^server/(?P<pk>\d+)/$', views.DetailView, name='detail'),
    url(r'^modify/(?P<pk>\d+)/$', views.resultView, name='resultView'),

    # Patching Tasks
    url(r'^tasks/', views.TasksView.as_view(), name='tasks'),
    # where the errata levels are set manually
    url(r'^errata/$', views.UpdateErrata),
    # Where excluded owners are set
    url(r'^owners/$', views.SetOwners),
    # Creates the .csv files
    url(r'^csv/', views.CreateCSV),
    # Clones a git repo and imports server info
    url(r'^git/', views.Git),
    # Unlinked url
    url(r'^unicorns/', views.Unicorns.as_view()),
    url(r'^security/', views.security),

    # Satellite links
    url(r'^satid/', views.SatId),
    url(r'^satupdates/', views.SatUpdates),

    # List views of hosts for the different environments
    url(r'^prod/$', views.ProdView),
    url(r'^stage/$', views.StageView),
    url(r'^qa/$', views.QAView),
    url(r'^dev/$', views.DevView),
]
