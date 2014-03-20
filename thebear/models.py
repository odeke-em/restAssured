# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Copyright (c) 2014

from django.db import models

# Local module
import theBearConstants

class Song(models.Model):
  title = models.CharField(max_length = theBearConstants.MAX_MISC_STR_LENGTH)
  artist = models.CharField(max_length = theBearConstants.MAX_MISC_STR_LENGTH)
  url = models.URLField(max_length = theBearConstants.MAX_MISC_STR_LENGTH)
  trackHash = models.CharField(
    max_length = theBearConstants.MAX_HASH_LENGTH, default=""
  )
  playTime = models.DecimalField(
    max_digits = theBearConstants.MAX_TIME_DIGITS,
    decimal_places=theBearConstants.MAX_DECIMAL_PLACES
  )
  dateCreated = models.DateTimeField(auto_now_add=True) # Auto-set by DB
  lastEditTime = models.DateTimeField(auto_now=True) # Automatically changed by DB

  def __unicode__(self):
    return "Song::{t}".format(t=self.title)
