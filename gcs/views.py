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

import gcs.models
import gcsConstants

# CSRF exemption only for development purposes
@csrf_exempt
def index(request):
  return markerHandler(request)

@csrf_exempt
def markerHandler(request):
  return crudAPI.handleHTTPRequest(
    request, gcsConstants.MARKER_TABLE_KEY, gcs.models
  )

@csrf_exempt
def imageHandler(request):
  return crudAPI.handleHTTPRequest(
    request, gcsConstants.IMAGE_TABLE_KEY, gcs.models
  )

@csrf_exempt
def labelHandler(request):
  return crudAPI.handleHTTPRequest(
    request, gcsConstants.LABEL_TABLE_KEY, gcs.models
  )
