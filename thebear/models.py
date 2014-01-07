# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Copyright (c) 2014

from django.db import models

import globalVariables as globVars

class PlayTime(models.Model):
  timeSinceEpoch = models.DecimalField(
    max_digits=globVars.MAX_DIGITS, decimal_places=globVars.MAX_DECIMAL_PLACES,
    unique = True
  )

  def __unicode__(self):
    return "%.4f"%(self.timeSinceEpoch)

class Song(models.Model):
  title = models.CharField(max_length = globVars.MAX_MISC_STR_LENGTH)
  artist = models.CharField(max_length = globVars.MAX_MISC_STR_LENGTH)
  url = models.URLField(max_length = globVars.MAX_MISC_STR_LENGTH)
  trackHash = models.CharField(
    max_length = globVars.MAX_HASH_LENGTH, default=""
  )

  def __unicode__(self):
    return "Song::{t}".format(t=self.title)

class SongEntry(models.Model):
  song = models.ForeignKey(Song)
  playTime = models.ForeignKey(PlayTime)

  def __unicode__(self):
    return "[%s:%s]"%(self.song, self.playTime)
