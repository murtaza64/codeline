from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateResponseMixin
from timeline.models import Post, Tag
from django.contrib.auth.models import User
from django.core import serializers
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
    tags = post.tags.all().order_by('name').order_by('-lang')
    send_post = {'id': post.id, 'title': post.title, 'author': post.author,
        'date': post.date, 'tags': tags, 'body': enumerate(cells)}
    print('assembled post')
    return send_post

class JSONPostViewMixin(TemplateResponseMixin):
    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('format') == 'json':
            return JsonResponse(
                dict(data=self.get_data(context)),
                **response_kwargs,
            )
        else:
            return super(JSONPostViewMixin, self).render_to_response(context, **response_kwargs)
    def get_data(self, context):
        qs = context['object_list']
        j = []
        for p in qs:
            d = {}
            d['pk'] = p.pk
            d['model'] = 'timeline.post'
            fields = {}
            fields['title'] = p.title
            fields['author'] = p.author.pk
            fields['tags'] = [t.id for t in p.tags.all()]
            fields['date'] = p.date
            fields['body'] = json.loads(p.body)
            d['fields'] = fields
            j.append(d)
        print(j)
        return j

class PostListView(JSONPostViewMixin, ListView):
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

class SinglePostView(JSONPostViewMixin, DetailView):
    template_name = 'timeline/post_view.html'
    model = Post

    def get_context_data(self, **kwargs):
        context = super(SinglePostView, self).get_context_data(**kwargs)
        context['post'] = assemble_post(context['object'])
        #HACK: make SinglePostView work nicely with JSONPostViewMixin
        context['object_list'] = [context['object']]
        context['subtitle'] = '/' + context['post']['title']
        context['title'] = '{} | codeli.ne'.format(context['post']['title'])
        return context

class UserTimelineView(PostListView):
    template_name = 'timeline/user.html'

    def get_queryset(self):
        qs = super(UserTimelineView, self).get_queryset()
        user = User.objects.get(username=self.kwargs['usr'])
        qs = qs.filter(author=user)
        return qs

    def get_context_data(self, **kwargs):
        print('USER TIMELINE VIEW')
        context = super(UserTimelineView, self).get_context_data(**kwargs)
        context['subtitle'] = '/user/' + self.kwargs['usr']
        context['title'] = '{}\'s codli.ne'.format(self.kwargs['usr'])
        return context

class TagTimelineView(PostListView):
    template_name = 'timeline/user.html'
    def get_queryset(self):
        tags = []
        queryset = []
        qs = super(TagTimelineView, self).get_queryset()
        tags = [Tag.objects.get(name=t) for t in [a for a in self.args if a]]
        qs = qs.filter(tags__in=tags)
        print(qs)
        return qs

    def get_context_data(self, **kwargs):
        args = [a for a in self.args if a]
        print('TAG TIMELINE VIEW')
        context = super(TagTimelineView, self).get_context_data(**kwargs)
        context['subtitle'] = '/tag/' + '+'.join(args)
        context['title'] = '+'.join(args) + ' | codeli.ne'
        return context

def new(request):
    return render(request, 'timeline/new.html', {'title':'new'})

#TODO: tags, ajax/live page updates
