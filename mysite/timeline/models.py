from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    class Meta:
        permissions = (
            ('delete_any', 'Can delete any post'),
            ('edit_any', 'Can edit any post')
        )
    title = models.CharField(max_length=140)
    body = models.TextField()
    date = models.DateTimeField()
    last_updated = models.DateTimeField()
    edited = models.BooleanField(default=False)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    parent = models.ForeignKey('Post', null=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField('Tag')
    private = models.BooleanField(default=False)
    def __str__(self):
        return self.title

class Tag(models.Model):
    name = models.CharField(max_length = 140)
    lang = models.BooleanField(default = 0)
    def __str__(self):
        return self.name
