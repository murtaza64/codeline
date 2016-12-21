from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.base import TemplateResponseMixin
from timeline.models import Post, Tag
from django.contrib.auth.models import User
from django.core import serializers
from django.template import RequestContext
from django.middleware.csrf import get_token
import json, re
import datetime
from markdown2 import markdown


def assemble_post(post):
    '''
    Takes a Post object and converts it into a format friendly
    to the template (unpacks post.body into an enumerated iterable
    of cell dicts).
    '''
    #print(post.body)
    if post.body:
        body_dict = json.loads(post.body)
    #print(body_dict)
        try:
            cells = [c for c in body_dict['cells']]
        except KeyError:
            cells = [dict(type=0, content='empty post')]
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
    else:
        cells = [dict(type=0, content='empty post')]

    tags = post.tags.all().order_by('-lang', 'name')
    send_post = {'id': post.id, 'title': post.title, 'author': post.author,
        'date': post.date, 'tags': tags, 'body': enumerate(cells)}
    #print('assembled post')
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
        #print(j)
        return j

class PostListView(JSONPostViewMixin, ListView):
    queryset = Post.objects.all().order_by('-date')
    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        context['posts'] = [assemble_post(post) for post in context['object_list']]
        return context

class GlobalTimelineView(PostListView):
    template_name = 'timeline/timeline.html'
    def get(self, *args, **kwargs):
        #import ipdb; ipdb.set_trace(context=9)
        return super(GlobalTimelineView, self).get(*args, **kwargs)
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
        #HACK: makes SinglePostView work nicely with JSONPostViewMixin
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

class NewPostView(TemplateView):
    template_name = 'timeline/new.html'
    def get_context_data(self, **kwargs):
        context = super(NewPostView, self).get_context_data(**kwargs)
        context['subtitle'] = '/new'
        context['title'] = 'new post | codeli.ne'
        c = RequestContext(self.request)
        print(context)
        print(c)
        return context
    def post(self, request, *args, **kwargs):
        newpost = Post()
        postdict = json.loads(str(request.body, 'utf-8'))
        try:
            newpost.author = User.objects.get(username=postdict['author'])
            newpost.title = postdict['title']
            newpost.date = datetime.datetime.now()
        except Exception as e:
            print('SOME VALIDATION ERROR')
            print(e)
            return JsonResponse(dict(error='true'))
        newpost.save()
        if not newpost.title:
            newpost.title = 'untitled '+str(newpost.id)
        tags = postdict['tagstring'].split()
        print(tags)
        for tag in tags:
            try:
                tag = ''.join([c for c in tag if c in 'abcdefghijklmnopqrstuvwxyz1234567890-_.'])
                tag_obj = Tag.objects.get(name=tag)
            except Tag.DoesNotExist:
                tag_obj = Tag()
                tag_obj.name = tag
                tag_obj.save()
            newpost.tags.add(tag_obj)
            print(tag)
        print(postdict['cells'])
        if (not postdict['cells']):
            newpost.delete()
            return JsonResponse(dict(success=False, error='empty post'))
        body = dict(cells=postdict['cells'])
        newpost.body = json.dumps(body)
        print(newpost)
        newpost.save()
        return JsonResponse(dict(success=True, link='http://'+request.get_host()+'/'+str(newpost.id)))


#TODO:40 tags, ajax/live page updates
