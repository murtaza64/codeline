from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length = 140)
    body = models.TextField()
    date = models.DateTimeField()
    author = models.ForeignKey(User, default = 1, on_delete = models.CASCADE)
    tags = models.ManyToManyField('Tag')
    def __str__(self):
        return self.title

class Tag(models.Model):
    name = models.CharField(max_length = 140)
    lang = models.BooleanField(default = 0)
    def __str__(self):
        return self.name