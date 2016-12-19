from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from timeline.models import Post
from django.contrib.auth.models import User
import json, re
from markdown2 import markdown

def assemble_post(post):
    #print(post.body)
    body_dict = json.loads(post.body)
    #print(body_dict)
    cells = [c for c in body_dict['cells']]
    for cell in cells:
        t = cell['content']
        if cell['type'] == 1:
            t = markdown(t)
            #print(t)
        if cell['type'] == 0:
            #print(t)
            t = re.sub(r'\n', '<br>', t)
            #print(t)
        cell['content'] = t
    send_post = {'id': post.id, 'title': post.title, 'author': post.author,
        'date': post.date, 'body': enumerate(cells)}
    print('assembled post')
    return send_post


class PostListView(ListView):
    queryset = Post.objects.all().order_by('-date')
    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        context['posts'] = [assemble_post(post) for post in context['object_list']]
        return context

class GlobalTimelineView(PostListView):
    template_name = 'timeline/timeline.html'
    def get_context_data(self, **kwargs):
        context = super(GlobalTimelineView, self).get_context_data(**kwargs)
        context['title'] = 'codeli.ne'
        return context

class SinglePostView(DetailView):
    template_name = 'timeline/post_view.html'
    model = Post

    def get_context_data(self, **kwargs):
        context = super(SinglePostView, self).get_context_data(**kwargs)
        context['post'] = assemble_post(context['object'])
        context['subtitle'] = '/' + context['post']['title']
        context['title'] = '{} | codei.ne'.format(context['post']['title'])
        return context

class UserTimelineView(PostListView):
    template_name = 'timeline/user.html'

    def get_queryset(self):
        qs = super(UserTimelineView, self).get_queryset()
        user = User.objects.get(username = self.kwargs['usr'])
        qs = qs.filter(author = user)
        return qs

    def get_context_data(self, **kwargs):
        print('USER TIMELINE VIEW')
        context = super(UserTimelineView, self).get_context_data(**kwargs)
        context['subtitle'] = '/user/' + self.kwargs['usr']
        context['title'] = '{}\'s codli.ne'.format(self.kwargs['usr'])
        return context

def new(request):
    return render(request, 'timeline/new.html', {'title':'new'})

#TODO: tags, ajax/live page updates
