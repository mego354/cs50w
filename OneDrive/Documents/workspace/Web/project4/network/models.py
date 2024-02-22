from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following_users', blank=True, null=True)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers_users', blank=True, null=True)
    image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    text = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    likers = models.ManyToManyField(User, blank=True, null=True)
    image = models.ImageField(upload_to='network/', blank=True, null=True)

