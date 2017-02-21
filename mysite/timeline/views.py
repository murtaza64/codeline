import datetime
import json
import re

from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core import serializers
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import redirect, render
from django.template import RequestContext
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.base import TemplateResponseMixin
from django.db.models.query import QuerySet
from django.db.models import Count
from markdown2 import markdown
from timeline.models import Post, Tag


def assemble_post(post):
    '''
    Takes a Post object and converts it into a format friendly
    to the template (unpacks post.body into an enumerated iterable
    of cell dicts).
    '''
    if post.body:
        body_dict = json.loads(post.body)
        try:
            cells = [c for c in body_dict['cells']]
        except KeyError:
            cells = [dict(type=0, content='empty post')]
        for cell in cells:
            t = cell['content']
            if cell['type'] == 1:
                t = markdown(t)
            if cell['type'] == 0:
                t = re.sub(r'\n', '<br>', t)
            cell['content'] = t
    else:
        cells = [dict(type=0, content='empty post')]

    tags = post.tags.all().order_by('-lang', 'name')
    send_post = {'id': post.id, 'title': post.title, 'author': post.author,
        'date': post.date, 'private': post.private, 'tags': tags, 'body': enumerate(cells)}
    return send_post

class JSONPostViewMixin(TemplateResponseMixin):

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('format') == 'json':
            return JsonResponse(
                dict(data=self.get_data(context)),
                **response_kwargs,
            )
        else:
            #print(context.keys())
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
            if p.author is not None:
                fields['author'] = p.author.username
            else:
                fields['author'] = None
            fields['tags'] = [{'name': t.name, 'lang': t.lang} for t in p.tags.all()]
            fields['date'] = p.date
            if p.body and p.body != '{}':
                fields['body'] = json.loads(p.body)
                for cell in fields['body']['cells']:
                    if cell['type'] == 2:
                        cell['is_code'] = True
            else:
                fields['body'] = {'cells':[]}
            fields['private'] = p.private
            d['fields'] = fields
            j.append(d)
        return j


class PostListView(JSONPostViewMixin, ListView):
    queryset = Post.objects.all().order_by('-date')
    paginate_by = 20 #TODO
    
    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        context['posts'] = [assemble_post(post) for post in context['object_list']]
        #context['posts'] = [p for p in context['posts'] if 
            #not(p['private']) or p['author'] is self.request.user]
        return context


class GlobalTimelineView(PostListView):
    template_name = 'timeline/timeline.html'

    def get(self, *args, **kwargs):
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
        context['subtitle'] = '/' + str(context['post']['id'])
        context['title'] = '{} | codeli.ne'.format(context['post']['title'])
        return context


class UserTimelineView(PostListView):
    template_name = 'timeline/timeline.html'

    def get_queryset(self):
        qs = super(UserTimelineView, self).get_queryset()
        user = User.objects.get(username=self.kwargs['usr'])
        qs = qs.filter(author=user)
        return qs

    def get_context_data(self, **kwargs):
        print('USER TIMELINE VIEW')
        context = super(UserTimelineView, self).get_context_data(**kwargs)
        context['subtitle'] = '/user/' + self.kwargs['usr']
        context['title'] = '{}\'s codeli.ne'.format(self.kwargs['usr'])
        return context

class UserTitleTimelineView(UserTimelineView):
    
    def get_queryset(self):
        qs = super(UserTitleTimelineView, self).get_queryset()
        title = self.kwargs['title']
        qs = qs.filter(title__in=[title, title.replace('_', ' ')])
        return qs

class TagTimelineView(PostListView):
    template_name = 'timeline/timeline.html'

    def get_queryset(self):
        tagstr = self.kwargs['tagstr']
        tags = []
        queryset = []
        qs = super(TagTimelineView, self).get_queryset()
        for t in [a for a in tagstr.split('+') if a]:
            try:
                tags.append(Tag.objects.get(name=t))
            except Tag.DoesNotExist:
                pass
        qs = qs.filter(tags__in=tags)
        #print(qs)
        return qs

    def get_context_data(self, **kwargs):
        tagstr = self.kwargs['tagstr']
        print('TAG TIMELINE VIEW')
        context = super(TagTimelineView, self).get_context_data(**kwargs)
        context['subtitle'] = '/tag/' + tagstr
        context['title'] = tagstr + ' | codeli.ne'
        return context

class FilterTimelineView(PostListView):
    template_name = 'timeline/timeline.html'

    @staticmethod
    def update_score(posts, scoredict, score, qs):
        for post in posts:
            if post.id not in scoredict:
                scoredict[post.id] = score
                qs.append(post)
            else:
                scoredict[post.id] += score

    def get_queryset(self):
        print(self.request.GET)
        get = self.request.GET

        if 'title' not in get and 'user' not in get and 'tags' not in get:
            return Post.objects.all().order_by('-date')

        qs = []
        scoredict = {}

        if 'title' in get:
            title = get['title']
            posts = Post.objects.filter(title__in=[title, title.replace('_', ' ')])
            self.update_score(posts, scoredict, 1000, qs)
            posts = Post.objects.filter(title__contains=title)
            self.update_score(posts, scoredict, 900, qs)
            posts = Post.objects.filter(title__contains=title.replace('_', ' '))
            self.update_score(posts, scoredict, 900, qs)

        if 'user' in get:
            user = get['user']
            posts = Post.objects.filter(user=user)
            self.update_score(posts, scoredict, 500, qs)
            posts = Post.objects.filter(user__contains=user)
            self.update_score(posts, scoredict, 350, qs)

        if 'tags' in get:
            tagnames = [a for a in get['tags'].split() if a]
            tags = []
            for t in tagnames:
                try:
                    tags.append(Tag.objects.get(name=t))
                except Tag.DoesNotExist:
                    pass
            posts = list(Post.objects.filter(tags__in=tags).order_by('-date'))
            for post in posts:
                matching_tags = len([t for t in post.tags.all() if t in tags])
            for post in posts:
                if post.id not in scoredict:
                    qs.append(post)
                    scoredict[post.id] = 20*matching_tags
                else:
                    scoredict[post.id] += 20*matching_tags

        qs = [post for post in sorted(qs, key=lambda i: scoredict[i.id], reverse=True)]
        return qs

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
            print('USER', request.user, request.user.is_authenticated)
            print(postdict)
            if request.user.is_authenticated and not postdict['anonymous']:
                print('user is authenticated')
                newpost.author = request.user
            else:
                newpost.author = None
            newpost.title = postdict['title']
            newpost.date = datetime.datetime.now()
        except Exception as e:
            print('SOME VALIDATION ERROR')
            print(e)
            return JsonResponse(dict(success=False))
        newpost.save()
        if not newpost.title:
            newpost.title = 'untitled '+str(newpost.id)
        tags = postdict['tagstring'].lower().strip().split()
        print(tags)
        for tag in tags:
            tag = ''.join([c for c in tag if c in 'abcdefghijklmnopqrstuvwxyz1234567890-_.'])
            tag_obj = Tag.objects.get_or_create(name=tag, defaults={'lang': False})[0]
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

def live_view(request):
    return render(request, 'timeline/live.html', {
        'title': 'codeli.ne',
        'subtitle': '/live'
    })

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST) #TODO custom user form
        if form.is_valid():
            return redirect('/login')
    if request.method == 'GET':
        form = UserCreationForm() #TODO attrs={'class': 'loginfield'}
    print(form)
    return render(request, 'timeline/register.html', {
        'form': form, 
        'title': 'register | codeli.ne',
        'subtitle': '/register'
    })

def logout_view(request):
    logout(request)
    return redirect('/')

#TODO:40 tags, ajax/live page updates
