from django.conf.urls import url, patterns, include
from . import views
#from django.views.generic import ListView
from django.views.generic import ListView, DetailView
from autopatch.models import Server, Post
from django.conf.urls.static import static

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns = [
    url(r'^$', ListView.as_view(
        queryset=Post.objects.all().order_by("-date")[:25],
        template_name="autopatch/base.html")),
    url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^prod/$', views.ProdView.as_view()),
    url(r'^stage/$', views.StageView.as_view()),
    url(r'^qa/$', views.QAView.as_view()),
    url(r'^dev/$', views.DevView.as_view()),
    url(r'^tasks/', views.TasksView.as_view()),
    url(r'^home/$', views.Home, name='Home'),
    url(r'^form_upload.html/$',
        views.post_form_upload, name='post_form_upload'),
    url(r'create/$', views.create),
    url(r'genlist/$', views.GetList),
    url(r'hostlist/$', views.AllHosts.as_view()),
    #url(r'^{{ Server.server }}/$', views.DetailView.as_view(), name='detail'),
    #url(r'^archives/$', views.ArchiveView.as_view()),
    #url(r'^latestnews/$', views.LatestView.as_view()),
    #url(r'^$', views.index, name='index'),
    # # ex: /polls/5/
    # url(r'^(?P<question_id>[0-9]+)/$', views.detail, name='detail'),
    # # ex: /polls/5/results/
    # url(r'^(?P<question_id>[0-9]+)/results/$', views.results, name='results'),
    # # ex: /polls/5/vote/
    # url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
    # url(r'^specifics/(?P<question_id>[0-9]+)/$', views.detail, name='detail'),
    # # ex: /polls/5/results/
    # url(r'^(?P<question_id>[0-9]+)/results/$', views.results, name='results'),
    # # ex: /polls/5/vote/
    # url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
    #url(r'^$', views.IndexView.as_view(), name='index'),
    #url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    #url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
    #url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
    # url(r'^(?P<pk>\d+)$', DetailView.as_view(
    #     model = Post,
    #     template_name="autopatch/post.html"))
]
