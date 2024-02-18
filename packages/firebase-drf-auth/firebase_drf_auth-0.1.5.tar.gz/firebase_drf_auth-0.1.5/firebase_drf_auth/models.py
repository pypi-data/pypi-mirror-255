from django.db import models
from django.contrib.auth import get_user_model

class UserFirebase(get_user_model()):
    uid_firebase = models.CharField(max_length=255)
