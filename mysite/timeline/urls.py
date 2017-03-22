from django.conf.urls import url
from django.views.generic import ListView, DetailView
from timeline.models import Post
import timeline.views as views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', views.live_view, name='live'),
    url(r'^filter/?$', views.FilterTimelineView.as_view(), name='filter'),
    url(r'^global/?$', views.GlobalTimelineView.as_view(), name='timeline'),
    url(r'^list/?$', views.PostListView.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/?$', views.SinglePostView.as_view(), name='post_view'),
    #url(r'^test/', views.test, name = 'test'),
    url(r'^new/?$', views.NewPostView.as_view(), name='new'),
    url(r'^user/(?P<usr>[a-zA-Z0-9.\-_]+)/?$', views.UserTimelineView.as_view(), name='user'),
    url(r'^user/(?P<usr>[a-zA-Z0-9.\-_]+)/(?P<title>[a-zA-Z0-9.\-()\[\]{}_]+)$', views.UserTitleTimelineView.as_view(), name='user_title'),
    url(r'^tag/(?P<tagstr>[a-zA-Z0-9.\-_+]+)$', views.TagTimelineView.as_view(), name='tag'),
    url(r'^login/?$', auth_views.login, 
    {
        'template_name': 'timeline/login.html',
        'extra_context': {
            'title': 'login | codeli.ne',
            'subtitle': '/login'
        }
    }, name='login'),
    url(r'^register/$', views.register_view, name='register'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^delete/(?P<pk>\d+)/?$', views.delete_view, name='delete')
]
