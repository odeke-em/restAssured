# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Copyright (c) 2014

from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
  url(r'^/', views.index, name='index'),
  url(r'^index|^$', views.index, name='index'),
  url(r'^forumHandler', views.forumHandler, name='forumHandler'),
  url(r'^blogPostHandler', views.blogPostHandler, name='blogPostHandler'),
  url(r'^coreUserHandler', views.coreUserHandler, name='coreUserHandler'),
  url(r'^forumPostHandler', views.forumPostHandler, name='forumPostHandler'),
  url(r'^coreCommentHandler', views.coreCommentHandler, name='coreCommentHandler'),
  url(r'^forumForumPostHandler', views.forumForumPostHandler, name='forumForumPostHandler'),
)
