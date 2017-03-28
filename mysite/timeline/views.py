import datetime
import json
import re

from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import redirect, render, get_object_or_404
from django.template import RequestContext
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.base import TemplateResponseMixin 
from django.views.generic.detail import SingleObjectMixin
from django.db.models.query import QuerySet
from django.db.models import Count
from markdown2 import markdown
from timeline.models import Post, Tag


def assemble_post(post, request):
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
        'date': post.date, 'last_updated': post.last_updated, 'edited': post.edited, 
        'private': post.private, 'author_logged_in': request.user == post.author,
        'parent': post.parent, 'tags': tags, 'body': enumerate(cells)}
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
            fields['author_logged_in'] = self.request.user == p.author
            fields['id'] = p.id
            fields['title'] = p.title
            if p.author is not None:
                fields['author'] = p.author.username
            else:
                fields['author'] = None
            fields['tags'] = [{'name': t.name, 'lang': t.lang} for t in p.tags.all()]
            fields['date'] = p.date
            fields['edited'] = p.edited
            fields['last_updated'] = p.last_updated
            if p.parent:
                fields['parent'] = dict(title=p.parent.title, id=p.parent.id)
            else:
                fields['parent'] = None
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
        context['posts'] = [assemble_post(post, self.request) for post in context['object_list']]
        #context['posts'] = [p for p in context['posts'] if 
            #not(p['private']) or p['author'] is self.request.user]
        return context


class GlobalTimelineView(PostListView):
    template_name = 'timeline/timeline.html'

    def get(self, *args, **kwargs):
        return super(GlobalTimelineView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GlobalTimelineView, self).get_context_data(**kwargs)
        context['title'] = 'codeline'
        return context

class SinglePostView(JSONPostViewMixin, DetailView):
    template_name = 'timeline/post_view.html'
    model = Post

    def get_context_data(self, **kwargs):
        context = super(SinglePostView, self).get_context_data(**kwargs)
        context['post'] = assemble_post(context['object'], self.request)
        #HACK: makes SinglePostView work nicely with JSONPostViewMixin
        context['object_list'] = [context['object']]
        context['subtitle'] = '/' + str(context['post']['id'])
        context['title'] = '{} | codeline'.format(context['post']['title'])
        return context


class UserTimelineView(PostListView):
    template_name = 'timeline/timeline.html'

    def get_queryset(self):
        qs = super(UserTimelineView, self).get_queryset()
        user = get_object_or_404(User, username=self.kwargs['usr'])
        qs = qs.filter(author=user)
        return qs

    def get_context_data(self, **kwargs):
        #print('USER TIMELINE VIEW')
        context = super(UserTimelineView, self).get_context_data(**kwargs)
        context['subtitle'] = '/user/' + self.kwargs['usr']
        context['title'] = '{}\'s codeline'.format(self.kwargs['usr'])
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
        #print('TAG TIMELINE VIEW')
        context = super(TagTimelineView, self).get_context_data(**kwargs)
        context['subtitle'] = '/tag/' + tagstr
        context['title'] = tagstr + ' | codeline'
        return context

class ForksView(PostListView):
    template_name = 'timeline/forks.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subtitle'] = '/' + str(self.parent.id) + '/forks'
        context['title'] =  'forks of ' + self.parent.title + ' | codeline'
        context['parent'] = self.parent
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(parent=self.parent)
        return qs

    def get(self, request, *args, **kwargs):
        self.parent = get_object_or_404(Post, pk=kwargs['pk'])
        return super().get(request, *args, **kwargs)

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
        #print(self.request.GET)
        get = self.request.GET
        if not (get.get('title', False) or get.get('user', False) or get.get('tags', False)):
            return Post.objects.all().order_by('-date')
        
        qs = []
        scoredict = {}
        posts_minusdate = Post.objects.order_by('-date')
        if 'title' in get and get['title']:
            title = get['title']
            posts = posts_minusdate.filter(title__in=[title, title.replace('_', ' ')])
            self.update_score(posts, scoredict, 1000, qs)
            posts = posts_minusdate.filter(title__contains=title)
            self.update_score(posts, scoredict, 900, qs)
            posts = posts_minusdate.filter(title__contains=title.replace('_', ' '))
            self.update_score(posts, scoredict, 900, qs)

        if 'user' in get and get['user']:
            user = get['user']
            posts = posts_minusdate.filter(author__username=user)
            self.update_score(posts, scoredict, 500, qs)
            posts = posts_minusdate.filter(author__username__contains=user)
            self.update_score(posts, scoredict, 350, qs)

        if 'tags' in get and get['tags']:
            tagnames = [a for a in get['tags'].split() if a]
            tags = []
            for t in tagnames:
                try:
                    tags.append(Tag.objects.get(name=t))
                except Tag.DoesNotExist:
                    pass
            posts = list(posts_minusdate.filter(tags__in=tags))
            for post in posts:
                matching_tags = len([t for t in post.tags.all() if t in tags])
            for post in posts:
                if post.id not in scoredict:
                    qs.append(post)
                    scoredict[post.id] = 20*matching_tags
                else:
                    scoredict[post.id] += 20*matching_tags

        qs = [post for post in sorted(qs, key=lambda i: scoredict[i.id], reverse=True)]
        #print(qs, scoredict)
        return qs

class NewPostView(TemplateView):
    template_name = 'timeline/new.html'

    def get_context_data(self, **kwargs):
        context = super(NewPostView, self).get_context_data(**kwargs)
        context['subtitle'] = '/new'
        context['title'] = 'new post | codeline'
        return context

    def update_post(self, request, post):
        postdict = json.loads(str(request.body, 'utf-8'))
        try:
            if not post.author:
                if request.user.is_authenticated and not postdict['anonymous']:
                    post.author = request.user
                else:
                    post.author = None
            post.title = postdict['title']
            post.last_updated = datetime.datetime.now()
            if not post.date:
                post.date = post.last_updated
        except Exception as e:
            print('SOME VALIDATION ERROR')
            print(e)
            return (False, 'unknown', post.id)
        post.save()
        if not post.title:
            post.title = 'untitled '+str(post.id)
        tags = postdict['tagstring'].lower().strip().split()
        if (not postdict['cells']):
            return (False, 'empty post', post.id)
        body = dict(cells=postdict['cells'])
        post.body = json.dumps(body)
        post.tags.clear()
        for cell in body['cells']:
            if cell['lang'] and cell['type'] == 2:
                tag_obj = Tag.objects.get_or_create(name=cell['lang'].lower(), defaults={'lang': True})[0] #TODO
                post.tags.add(tag_obj)
        for tag in tags:
            tag = ''.join([c for c in tag if c in 'abcdefghijklmnopqrstuvwxyz1234567890-_.'])
            tag_obj = Tag.objects.get_or_create(name=tag, defaults={'lang': False})[0]
            post.tags.add(tag_obj)
        if not post.tags.all():
            post.tags.add(Tag.objects.get(name='untagged'))
        post.save()
        return (True, '', post.id)

    def post(self, request, *args, **kwargs):
        newpost = Post()
        # print(request.body)
        status = self.update_post(request, newpost)
        if status[0]:
            return JsonResponse(dict(
                success=True, 
                message = 'post created', 
                link='http://'+request.get_host()+'/'+str(status[2])
            ))
        else:
            return JsonResponse(dict(success=False, error=status[1]))

class ForkPostView(NewPostView, SingleObjectMixin):
    template_name = 'timeline/fork.html'
    model = Post

    def get_context_data(self, **kwargs):
        context = super(NewPostView, self).get_context_data(**kwargs)
        post = self.object
        if post.body:
            body_dict = json.loads(post.body)
            try:
                cells = [c for c in body_dict['cells']]
            except KeyError:
                cells = []
        else:
            cells = []
        tags = post.tags.all().order_by('-lang', 'name')
        send_post = {'id': post.id, 'title': post.title, 'author': post.author,
        'date': post.date, 'last_updated': post.last_updated, 'edited': post.edited, 
        'private': post.private, 'author_logged_in': self.request.user == post.author,
        'parent': post.parent, 'tags': tags, 'body': enumerate(cells)}

        context['post'] = send_post
        context['subtitle'] = '/fork/'+str(context['post']['id'])
        context['title'] = 'fork post | codeline'   
        return context 

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        response = super().get(request, *args, **kwargs)
        return response

    def post(self, request, *args, **kwargs):
        newpost = Post()
        status = self.update_post(request, newpost)
        newpost.parent = self.get_object()
        newpost.save()
        if status[0]:
            return JsonResponse(dict(
                success=True, 
                message='post forked', 
                link='http://'+request.get_host()+'/'+str(status[2])
            ))
        else:
            return JsonResponse(dict(success=False, message=status[1]))

class EditPostView(ForkPostView):
    template_name = 'timeline/edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['subtitle'] = '/edit/'+str(context['post']['id'])
        context['title'] = 'edit post | codeline'  
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user.is_authenticated and self.object.author == request.user:
            response = super().get(request, *args, **kwargs)
            return response
        else:
            return redirect('/'+str(self.object.id))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.is_authenticated or self.object.author != request.user:
            return JsonResponse(dict(success=False, message='User not authenticated'))
        else:
            status = self.update_post(request, self.object)
            self.object.edited = True
            self.object.save()
            if status[0]:
                return JsonResponse(dict(
                    success=True, 
                    message='post updated', 
                    link='http://'+request.get_host()+'/'+str(status[2])
                ))
            else:
                return JsonResponse(dict(success=False, message=status[1]))

def live_view(request):
    return render(request, 'timeline/live.html', {
        'title': 'codeline',
        'subtitle': '/live'
    })

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST) #TODO custom user form
        if form.is_valid():
            form.save()
            return redirect('/login')
    if request.method == 'GET':
        form = UserCreationForm() #TODO attrs={'class': 'loginfield'}
    #print(form)
    return render(request, 'timeline/register.html', {
        'form': form, 
        'title': 'register | codeline',
        'subtitle': '/register'
    })

def logout_view(request):
    logout(request)
    return redirect('/')

def delete_view(request, pk=None):
    if pk is None or not request.user.is_authenticated:
        return redirect('/')
    post = get_object_or_404(Post, pk=pk)
    if request.user == post.author:
        post.delete()
        return redirect(reverse('timeline:user', kwargs={'usr': request.user.username}))
    else:
        return redirect('/')

#TODO:40 tags, ajax/live page updates
