from django.shortcuts import render, redirect
from timeline.models import Post
from django.contrib.auth.models import User
import json, re
from markdown2 import markdown

def assemble_posts(posts):
    send_posts = []
    for post in posts:
        print(post.body)
        body_dict = json.loads(post.body)
        print(body_dict)
        cells = [c for c in body_dict['cells']]
        for cell in cells:
            t = cell['content']
            if cell['type'] == 1:
                t = markdown(t)
                print(t)
            if cell['type'] == 0:
                print(t)
                t = re.sub(r'\n', '<br>', t)
                print(t)
            cell['content'] = t
        send_posts.append((post, enumerate(cells)))
    return send_posts

def timeline(request):
    posts = Post.objects.all().order_by("-date")
    send_posts = assemble_posts(posts)
    return render(request, 'timeline/timeline.html', {
        'title':'timeline',
        'posts':send_posts
    })


def test(request):
    return render(request, 'timeline/test.html', {
        'title':'test',
        'r':range(50)
    })

def post_view(request, pk):
    posts = Post.objects.filter(pk=pk)
    send_posts = assemble_posts(posts)
    return render(request, 'timeline/post_view.html', {
        'post':send_posts[0],
        'title':send_posts[0][0].title
    })

def new(request):
    return render(request, 'timeline/new.html', {'title':'new'})

def user(request, usr):
    user = User.objects.get(username=usr)
    posts = Post.objects.filter(author=user).order_by("-date")
    send_posts = assemble_posts(posts)
    return render(request, 'timeline/user.html', {
        'title':user.username,
        'user':user,
        'posts':send_posts
    })
#TODO: tags, ajax/live page updates
