# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Copyright (c) 2014

from django.db import models

# Local module
import theBearConstants

class PlayTime(models.Model):
  timeSinceEpoch = models.DecimalField(
    max_digits = theBearConstants.MAX_TIME_DIGITS,
    decimal_places=theBearConstants.MAX_DECIMAL_PLACES,unique = True
  )

  def __unicode__(self):
    return "%.4f"%(self.timeSinceEpoch)

class Song(models.Model):
  title = models.CharField(max_length = theBearConstants.MAX_MISC_STR_LENGTH)
  artist = models.CharField(max_length = theBearConstants.MAX_MISC_STR_LENGTH)
  url = models.URLField(max_length = theBearConstants.MAX_MISC_STR_LENGTH)
  trackHash = models.CharField(
    max_length = theBearConstants.MAX_HASH_LENGTH, default=""
  )
  dateCreated = models.DateField(auto_now_add=True) # Auto-set by DB
  lastEditTime = models.DateField(auto_now=True) # Automatically changed by DB

  def __unicode__(self):
    return "Song::{t}".format(t=self.title)

class SongEntry(models.Model):
  song = models.ForeignKey(Song)
  playTime = models.ForeignKey(PlayTime)
  dateCreated = models.DateField(auto_now_add=True)
  lastEditTime = models.DateField(auto_now=True)

  def __unicode__(self):
    return "[%s:%s]"%(self.song, self.playTime)
