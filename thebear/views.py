# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Copyright (c) 2013


from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest

import crudAPI
import globalVariables as globVars

def index(request):
  return HttpResponse("Freaky")

# CSRF exemption only for development purposes
@csrf_exempt
def songHandler(request):
  return crudAPI.handleHTTPRequest(request, globVars.SONG_TABLE_KEY)

@csrf_exempt
def playTimeHandler(request):
  return crudAPI.handleHTTPRequest(request, globVars.PLAYTIME_TABLE_KEY)

@csrf_exempt
def entryHandler(request):
  return crudAPI.handleHTTPRequest(request, globVars.SONGENTRY_TABLE_KEY)
