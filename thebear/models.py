# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Copyright (c) 2014

from django.db import models

# Local module
import theBearConstants

class Artist(models.Model):
    name = models.CharField(max_length=theBearConstants.MAX_MISC_STR_LENGTH)
    uri  = models.CharField(max_length=theBearConstants.MAX_MISC_STR_LENGTH, blank=True)
    extraInfo = models.CharField(max_length=theBearConstants.MAX_MISC_STR_LENGTH, blank=True)

    dateCreated = models.DateTimeField(auto_now_add=True) # Auto-set by DB
    lastEditTime = models.DateTimeField(auto_now=True) # Automatically changed by DB

    def __unicode__(self):
        return "Artist:{n}".format(n=self.name)

class Song(models.Model):
    title = models.CharField(max_length = theBearConstants.MAX_MISC_STR_LENGTH)
    artist = models.ForeignKey(Artist)
    uri = models.URLField(max_length = theBearConstants.MAX_MISC_STR_LENGTH, blank=True)
    playTime = models.DecimalField(
        max_digits = theBearConstants.MAX_TIME_DIGITS,
        decimal_places=theBearConstants.MAX_DECIMAL_PLACES
    )

    dateCreated = models.DateTimeField(auto_now_add=True) # Auto-set by DB
    lastEditTime = models.DateTimeField(auto_now=True) # Automatically changed by DB

    def __unicode__(self):
        return "Song::{t}".format(t=self.title)

