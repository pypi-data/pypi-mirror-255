from django.db import models
from django.contrib.auth import get_user_model

class Uid(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    uid = models.CharField(max_length=255)
