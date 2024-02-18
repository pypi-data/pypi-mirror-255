from rest_framework import authentication
from rest_framework import exceptions
import jwt
import firebase_admin
from firebase_admin import auth
from django.conf import settings

from .models import UserFirebase


firebase_app = firebase_admin.initialize_app()

class FirebaseJWTAuth(authentication.BaseAuthentication):
    def authenticate(self, request):
        verify_id_token = request.headers.get("X-Firebase-AppCheck", default="")
        try:
            decoded_token = auth.verify_id_token(verify_id_token)
            user, _ = UserFirebase.objects.get_or_create(uid_firebase=decoded_token["uid"])
        except (KeyError, ValueError, jwt.exceptions.DecodeError) as e:
            print(e)
            if settings.FIREBASE_AUTH_STRICT:
                raise exceptions.AuthenticationFailed("Invalid token")
            return None
        return user, decoded_token
