import sys
import time
import random
import hashlib
from django.db import models
import django.contrib.auth as djangoAuth

# Local module
import authConstants

pyVersion = sys.hexversion//(1<<24)
encodingKwargs = {}
if pyVersion >= 3:
    encodingKwargs = {'encoding': 'utf-8'}

class App(models.Model):
    meta = models.CharField(max_length=authConstants.MAX_META_LENGTH)
    name = models.CharField(max_length=authConstants.MAX_APPNAME_LENGTH, unique=True)
    _accessId = models.CharField(max_length=authConstants.MAX_ACCESSID_LENGTH, unique=True) # Indicate untouchability purpose with '_' prefix

    def save(self, *args, **kwargs):
        if not self.id: # First time this object is being saved
            self._accessId = hashlib.sha256(bytes(
                '%s%f%f%s'%(self.meta, time.time(), random.random(), self.name), **encodingKwargs
            )).hexdigest()

        super(App, self).save(*args, **kwargs)

class AuthUser(models.Model):
    app =  models.ForeignKey(App)
    djangoUser = models.ForeignKey(djangoAuth.models.User)

    meta = models.CharField(max_length=authConstants.MAX_META_LENGTH)

    dateCreated  = models.DateTimeField(auto_now_add=True)
    lastEditTime = models.DateTimeField(auto_now=True) # Automatically changed by DB
