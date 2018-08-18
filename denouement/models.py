from django.db import models
from django.contrib.auth.models import User

class ProfilePicture(models.Model):
    image = models.ImageField(upload_to="user_images")

class ForumCategory(models.Model):
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=200)

class ForumThread(models.Model):
    title = models.CharField(max_length=100)
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='category')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='thread_author')
    post_count = models.IntegerField(default=1)
    date = models.DateTimeField()

class ForumPost(models.Model):
    text = models.CharField(max_length=60000)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_author')
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name='thread')
    upvotes = models.IntegerField(default=0)
    date = models.DateTimeField()
