from django.db import models
import django.contrib.auth as djangoAuth

# Local module
import authConstants

class AuthUser(models.Model):
    appName =  models.CharField(max_length=authConstants.MAX_APPNAME_LENGTH)
    djangoUser = models.ForeignKey(djangoAuth.models.User)

    meta = models.CharField(max_length=authConstants.MAX_META_LENGTH)

    dateCreated  = models.DateTimeField(auto_now_add=True)
    lastEditTime = models.DateTimeField(auto_now=True) # Automatically changed by DB
