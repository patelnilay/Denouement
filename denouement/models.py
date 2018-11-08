from django.db import models
from django.contrib.auth.models import User

class ForumCategory(models.Model):
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=200)

class ForumThread(models.Model):
    title = models.CharField(max_length=100)
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='category')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='thread_author')
    post_count = models.IntegerField(default=1)
    date = models.DateTimeField()
    locked = models.BooleanField(default=False)
    pinned = models.BooleanField(default=False)

class ForumPost(models.Model):
    text = models.CharField(max_length=60000)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_author')
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name='thread')
    upvotes = models.IntegerField(default=0)
    date = models.DateTimeField()

    class Meta(object):
        permissions = (
            ("denouement.lock_forumthread", "Can lock threads"),
            ("denouement.pin_forumthread", "Can pin threads"),

        )

class ProfileComment(models.Model):
    text = models.CharField(max_length=60000)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_author')
    profile_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile_owner')
    date = models.DateTimeField()