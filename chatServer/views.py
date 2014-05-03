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

import chatServer.models
import chatServerConstants

# CSRF exemption only for development purposes
@csrf_exempt
def receipientHandler(request):
    return crudAPI.handleHTTPRequest(request, chatServerConstants.RECEIPIENT_TABLE_KEY, chatServer.models)

# CSRF exemption only for development purposes
@csrf_exempt
def messageMarkerHandler(request):
    return crudAPI.handleHTTPRequest(request, chatServerConstants.MESSAGE_MARKER_TABLE_KEY, chatServer.models)

# CSRF exemption only for development purposes
@csrf_exempt
def messageHandler(request):
    return crudAPI.handleHTTPRequest(request, chatServerConstants.MESSAGE_TABLE_KEY, chatServer.models)
