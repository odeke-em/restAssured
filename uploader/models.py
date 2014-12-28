# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Copyright (c) 2014
# Author: Emmanuel Odeke <odeke@ualberta.ca>

import uuid
from django.db import models

# Local module
import uploaderConstants

generateUUID = uuid.uuid4

class MultiPart(models.Model):
  __etag = models.CharField(max_length=uploaderConstants.MAX_CHECKSUM_LENGTH) 
  checkSumAlgoName = models.CharField(
                max_length=uploaderConstants.MAX_ALGONAME_LENGTH, default='sha256')
  dateCreated = models.DateTimeField(auto_now_add=True) # Automatically set on first object creation
  lastEditTime = models.DateTimeField(auto_now=True) # Automatically set after every save

  def __unicode__(self):
    return "MultiPart::{u}".format(u=self.__etag)

  def save(self, *args, **kwargs):
    if not self.id: # First time this object is being saved
      self.__etag = generateUUID().hex

    super(MultiPart, self).save(*args, **kwargs)


class Blob(models.Model):
  title = models.CharField(max_length=uploaderConstants.MAX_MISC_STR_LENGTH)
  author = models.CharField(max_length=uploaderConstants.MAX_MISC_STR_LENGTH)

  # Could be a local path or a url
  # Intentionally avoiding Django's models.URLField to avoid restrictions on path
  # explicitly having to be a URL ie http://www.*.domain
  uri = models.CharField(max_length=uploaderConstants.MAX_MISC_STR_LENGTH)

  # Auxilliary/Meta Information
  metaData = models.CharField(
            max_length=uploaderConstants.MAX_COMMENT_LENGTH, blank=True) # Optional

  content = models.FileField(upload_to='documents')
  parent = models.ForeignKey('Blob', null=True)

  size = models.IntegerField(default=0, blank=True)
  checkSum = models.CharField(max_length=uploaderConstants.MAX_CHECKSUM_LENGTH)
  encoding = models.CharField(max_length=uploaderConstants.MAX_ENCODING_STR_LENGTH,
                                                        default='utf-8', blank=True)
  checkSumAlgoName = models.CharField(
                  max_length=uploaderConstants.MAX_ALGONAME_LENGTH, default='sha256')

  dateCreated = models.DateTimeField(auto_now_add=True) # Automatically set on first object creation
  lastEditTime = models.DateTimeField(auto_now=True) # Automatically set after every save
  multipart = models.ForeignKey('MultiPart', null=True)

  def __unicode__(self):
    return "Blob::{t}{a} {e}".format(t=self.title, a=self.author, e=self.encoding)
