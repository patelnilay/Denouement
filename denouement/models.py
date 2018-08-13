from django.db import models

class ProfilePicture(models.Model):
    image = models.ImageField(upload_to="user_images")