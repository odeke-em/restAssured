# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Copyright (c) 2014

from django.db import models

# Local module
import gcsConstants

class Image(models.Model):
  title = models.CharField(max_length=gcsConstants.MAX_MISC_STR_LENGTH)

  # Who added the image
  author = models.CharField(max_length=gcsConstants.MAX_MISC_STR_LENGTH)

  # Could be a local path or a url
  # Intentionally avoiding Django's models.URLField to avoid restrictions on path
  # explicitly having to be a URL ie http://www.*.domain
  uri = models.CharField(max_length=gcsConstants.MAX_MISC_STR_LENGTH)

  dateCreated = models.DateTimeField(auto_now_add=True) # Automatically set on first object creation
  lastTimeEdit = models.DateTimeField(auto_now=True) # Automatically set after every save

  # Auxilliary/Meta Information
  metaData = models.CharField(max_length=gcsConstants.MAX_COMMENT_LENGTH, blank=True) # Optional

  # Binary data if required to save in the DB
  blob = models.CharField(max_length=gcsConstants.MAX_BLOB_LENGTH_BYTES, blank=True) # Optional

  phi = models.DecimalField(
    max_digits=gcsConstants.MAX_DIGITS, decimal_places=gcsConstants.MAX_DECIMAL_PLACES,
    default=0.0
  )

  time = models.DecimalField(
    max_digits=gcsConstants.MAX_DIGITS, decimal_places=gcsConstants.MAX_DECIMAL_PLACES,
    default=0.0
  )

  psi = models.DecimalField(
    max_digits=gcsConstants.MAX_DIGITS, decimal_places=gcsConstants.MAX_DECIMAL_PLACES,
    default=0.0
  )

  theta = models.DecimalField(
    max_digits=gcsConstants.MAX_DIGITS, decimal_places=gcsConstants.MAX_DECIMAL_PLACES,
    default=0.0
  )

  alt = models.DecimalField(
    max_digits=gcsConstants.MAX_DIGITS, decimal_places=gcsConstants.MAX_DECIMAL_PLACES,
    default=0.0
  )

  course = models.DecimalField(
    max_digits=gcsConstants.MAX_DIGITS, decimal_places=gcsConstants.MAX_DECIMAL_PLACES,
    default=0.0
  )

  speed = models.DecimalField(
    max_digits=gcsConstants.MAX_DIGITS, decimal_places=gcsConstants.MAX_DECIMAL_PLACES,
    default=0.0
  )

  utm_east = models.DecimalField(
    max_digits=gcsConstants.MAX_DIGITS, decimal_places=gcsConstants.MAX_DECIMAL_PLACES,
    default=0.0
  )

  utm_north = models.DecimalField(
    max_digits=gcsConstants.MAX_DIGITS, decimal_places=gcsConstants.MAX_DECIMAL_PLACES,
    default=0.0
  )

  pixel_per_meter = models.DecimalField(
    max_digits=gcsConstants.MAX_DIGITS, decimal_places=gcsConstants.MAX_DECIMAL_PLACES,
    default=0.0
  )

  ppm_difference = models.DecimalField(
    max_digits=gcsConstants.MAX_DIGITS, decimal_places=gcsConstants.MAX_DECIMAL_PLACES,
    default=0.0
  )

  def __unicode__(self):
    return "Image::{t}=>{p}".format(t=self.title, p=self.uri)

class Marker(models.Model):
  # Who added the marker usually the operator's name
  associatedImage = models.ForeignKey(Image)
  iconPath = models.CharField(max_length=gcsConstants.MAX_MISC_STR_LENGTH)
  author   = models.CharField(max_length=gcsConstants.MAX_MISC_STR_LENGTH)

  dateCreated = models.DateTimeField(auto_now_add=True) # Automatically set on first object creation
  lastTimeEdit = models.DateTimeField(auto_now=True) # Automatically set after every save

  # TODO: Define a robust tuple saving mechanism
  x = models.DecimalField(
   max_digits=gcsConstants.MAX_DIGITS, decimal_places=gcsConstants.MAX_DECIMAL_PLACES
  )
  y = models.DecimalField(
   max_digits=gcsConstants.MAX_DIGITS, decimal_places=gcsConstants.MAX_DECIMAL_PLACES
  )

  comments = models.CharField(max_length=gcsConstants.MAX_COMMENT_LENGTH, blank=True)

  def __unicode__(self):
    return "Marker::{a}=>@{d}".format(a=self.author, d=self.dateCreated)
