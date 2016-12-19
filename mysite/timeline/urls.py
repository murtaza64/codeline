from django.conf.urls import url
from django.views.generic import ListView, DetailView
from timeline.models import Post
import timeline.views as views

urlpatterns = [
    url(r'^$', views.GlobalTimelineView.as_view(), name = 'timeline'),
    url(r'^list/$', views.PostListView.as_view(), name = 'list'),
    url(r'^(?P<pk>\d+)$', views.SinglePostView.as_view(), name = 'post_view'),
    #url(r'^test/', views.test, name = 'test'),
    url(r'^new/', views.new, name='new'),
    url(r'^user/(?P<usr>\w+)$', views.UserTimelineView.as_view(), name='user')
]
