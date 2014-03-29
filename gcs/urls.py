# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Copyright (c) 2014

from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
  url(r'^/', views.index, name='index'),
  url(r'^index|^$', views.index, name='index'),
  url(r'^imageHandler', views.imageHandler, name='imageHandler'),
  url(r'^markerHandler', views.markerHandler, name='markerHandler'),
  url(r'^labelHandler', views.labelHandler, name='labelHandler'),
)
