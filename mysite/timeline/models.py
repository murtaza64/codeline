from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=140)
    body = models.TextField()
    date = models.DateTimeField()
    last_updated = models.DateTimeField(null=True)
    author = models.ForeignKey(User, default=1, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField('Tag')
    private = models.BooleanField(default=False)
    def __str__(self):
        return self.title

class Tag(models.Model):
    name = models.CharField(max_length = 140)
    lang = models.BooleanField(default = 0)
    def __str__(self):
        return self.name
