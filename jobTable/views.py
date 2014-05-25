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

import jobTable.models
import constants

# CSRF exemption only for development purposes
@csrf_exempt
def index(request):
  return jobHandler(request)

@csrf_exempt
def jobHandler(request):
    return crudAPI.handleHTTPRequest(
        request, constants.JOB_TABLE_KEY, jobTable.models
    )

@csrf_exempt
def workerHandler(request):
    return crudAPI.handleHTTPRequest(
        request, constants.WORKER_TABLE_KEY, jobTable.models
    )
