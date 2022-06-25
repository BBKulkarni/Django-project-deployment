from django.db import models
from django.urls import reverse
from django.conf import settings

from markdown import markdown
from groups.models import Group

from django.contrib.auth import get_user_model
User = get_user_model()

from django import template
register = template.Library()

# Create your models here.
class Post(models.Model):
    user = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    message = models.TextField()
    message_html = models.TextField(editable=False)
    group = models.ForeignKey(Group, related_name='posts', null=True, blank=True, on_delete=models.DO_NOTHING)
    members = models.ManyToManyField(User, through='Vote')
    objects = models.Manager()

    def __str__(self):
        return self.message

    def save(self, *args, **kwargs):
        self.message_html = markdown(self.message)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('posts:single', kwargs={'username':self.user.username, 'pk':self.pk})

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'message']

class Vote(models.Model):
    user = models.ForeignKey(User, related_name='user_votes', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='votes', on_delete=models.DO_NOTHING)
    objects = models.Manager()

    def __str__(self):
        return self.user

    class Meta:
        unique_together = ('user', 'post')