# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Copyright (c) 2014
# Uploader was inspired and examples taken from minimal-file-upload-django example by axelpale

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest

# Setting up path for API source
import sys, os
sys.path.append("api")
import crudAPI

import uploader.models
import uploaderConstants

from uploader.forms import DocumentForm

# CSRF exemption only for development purposes
@csrf_exempt
def index(request):
    return blobHandler(request)

@csrf_exempt
def blobHandler(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        print('request.POST', request.POST, request.FILES)
        print('validity', form.is_valid())
        if not form.is_valid():
            response = HttpResponse('Invalid form')
            response.status_code = 400
            return response
        else:
            print('createdFile')
            bodyContent = request.POST
            stringifyedContent =dict((str(k), str(v)) for k,v in bodyContent.items())
            createdFile = uploader.models.Blob(content=request.FILES['blob'], **stringifyedContent)
            print('createdFile', createdFile)
            response = HttpResponse()
            try:
                createdFile.save()
                response.status_code = 200
                response.status_message = 'Successful upload'
            except Exception, e:
                print('exception', e)
                response.status_code = 500
                response.status_message = 'Exception during uploading'

            return response
    else:
        return crudAPI.handleHTTPRequest(
            request, uploaderConstants.BLOB_TABLE_KEY, uploader.models
        )
