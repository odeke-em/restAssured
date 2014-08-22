# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Copyright (c) 2014

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest

# Setting up path for API source
import sys, os
sys.path.append("api")
import crudAPI

import core.models
import coreConstants

# CSRF exemption only for development purposes
@csrf_exempt
def index(request):
  return forumHandler(request)

@csrf_exempt
def forumHandler(request):
  return crudAPI.handleHTTPRequest(
    request, coreConstants.FORUM_TABLE_KEY, core.models
  )

@csrf_exempt
def coreUserHandler(request):
  return crudAPI.handleHTTPRequest(
    request, coreConstants.CORE_USER_TABLE_KEY, core.models
  )

@csrf_exempt
def blogPostHandler(request):
  return crudAPI.handleHTTPRequest(
    request, coreConstants.BLOG_POST_TABLE_KEY, core.models
  )

@csrf_exempt
def coreCommentHandler(request):
  return crudAPI.handleHTTPRequest(
    request, coreConstants.CORE_COMMENT_TABLE_KEY, core.models
  )

@csrf_exempt
def forumPostHandler(request):
  return crudAPI.handleHTTPRequest(
    request, coreConstants.FORUM_POST_TABLE_KEY, core.models
  )

@csrf_exempt
def forumForumPostHandler(request):
  return crudAPI.handleHTTPRequest(
    request, coreConstants.FORUM_FORUM_POST_TABLE_KEY, core.models
  )
