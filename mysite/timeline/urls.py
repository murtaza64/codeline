from django.conf.urls import url
from django.views.generic import ListView, DetailView
from timeline.models import Post
import timeline.views as views

urlpatterns = [
    url(r'^$', views.timeline, name = 'timeline'),
    url(r'^list/$',
        ListView.as_view(
            queryset = Post.objects.all().order_by("-date"),
            template_name = 'timeline/list.html'
        ),
        {
            'title':'list'
        },
    name = 'list'),
    url(r'^(?P<pk>\d+)$', views.post_view, name = 'post_view'),
    url(r'^test/', views.test, name = 'test'),
    url(r'^new/', views.new, name='new'),
    url(r'^user/(?P<usr>\w+)$', views.user, name='user')
]
