# Author: Emmanuel Odeke <odeke@ualberta.ca>

import sys
import time
import uuid
import random
import hashlib
from django.db import models
import django.contrib.auth as djangoAuth

# Local module
import authConstants

generateUUID = uuid.uuid4

class App(models.Model):
    meta = models.CharField(max_length=authConstants.MAX_META_LENGTH)
    name = models.CharField(max_length=authConstants.MAX_APPNAME_LENGTH, unique=True)
    _accessId = models.CharField(max_length=authConstants.MAX_ACCESSID_LENGTH, unique=True) # Indicate untouchability purpose with '_' prefix

    def save(self, *args, **kwargs):
        if not self.id: # First time this object is being saved
            self._accessId = generateUUID().hex

        super(App, self).save(*args, **kwargs)

class AuthUser(models.Model):
    app =  models.ForeignKey(App)
    djangoUser = models.ForeignKey(djangoAuth.models.User)

    meta = models.CharField(max_length=authConstants.MAX_META_LENGTH)

    dateCreated  = models.DateTimeField(auto_now_add=True)
    lastEditTime = models.DateTimeField(auto_now=True) # Automatically changed by DB

    _accessId = models.CharField(max_length=authConstants.MAX_ACCESSID_LENGTH, unique=True)
    _secretKey = models.CharField(max_length=authConstants.MAX_SECRETKEY_LENGTH, unique=True)

    def save(self, *args, **kwargs):
        if not self.id: # First save here
            self._accessId = generateUUID().hex
            self._secretKey = generateUUID().hex

        super(AuthUser, self).save(*args, **kwargs)
