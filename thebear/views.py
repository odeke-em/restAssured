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

import thebear.models
import theBearConstants

# CSRF exemption only for development purposes
@csrf_exempt
def index(request):
  return songHandler(request)

@csrf_exempt
def songHandler(request):
    return crudAPI.handleHTTPRequest(
        request, theBearConstants.SONG_TABLE_KEY, thebear.models
    )

@csrf_exempt
def artistHandler(request):
    return crudAPI.handleHTTPRequest( 
        request, theBearConstants.ARTIST_TABLE_KEY, thebear.models
    )
