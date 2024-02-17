from django.db import models
from django.contrib.auth import get_user_model

class Uid(get_user_model()):
    uid = models.CharField(max_length=255)
