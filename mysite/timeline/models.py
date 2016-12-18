from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length = 140)
    body = models.TextField()
    date = models.DateTimeField()
    author = models.ForeignKey(User, default = 1, on_delete = models.CASCADE)
    def __str__(self):
        return self.title
