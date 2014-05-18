# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Copyright (c) 2014

from django.db import models

# Local module
import uploaderConstants

class Blob(models.Model):
  title = models.CharField(max_length=uploaderConstants.MAX_MISC_STR_LENGTH)
  author = models.CharField(max_length=uploaderConstants.MAX_MISC_STR_LENGTH)

  # Could be a local path or a url
  # Intentionally avoiding Django's models.URLField to avoid restrictions on path
  # explicitly having to be a URL ie http://www.*.domain
  uri = models.CharField(max_length=uploaderConstants.MAX_MISC_STR_LENGTH)

  # Auxilliary/Meta Information
  metaData = models.CharField(max_length=uploaderConstants.MAX_COMMENT_LENGTH, blank=True) # Optional

  content = models.FileField(upload_to='documents') # , max_length=uploaderConstants.MAX_BLOB_LENGTH_BYTES)
  encoding = models.CharField(max_length=uploaderConstants.MAX_ENCODING_STR_LENGTH, default='utf-8', blank=True)

  dateCreated = models.DateTimeField(auto_now_add=True) # Automatically set on first object creation
  lastTimeEdit = models.DateTimeField(auto_now=True) # Automatically set after every save

  def __unicode__(self):
    return "Blob::{t}{a} {e}".format(t=self.title, a=self.author, e=self.encoding)
