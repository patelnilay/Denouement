from django.contrib import admin
from .models import ForumCategory, ForumThread, ForumPost, ProfileComment

admin.site.register(ForumCategory)
admin.site.register(ForumThread)
admin.site.register(ForumPost)
admin.site.register(ProfileComment)
