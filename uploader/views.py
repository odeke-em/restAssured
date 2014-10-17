# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Copyright (c) 2014
# Uploader was inspired and examples taken from minimal-file-upload-django example by axelpale

# This project's content links up with the file system and hence the only method that will use
# crudAPI will be 'GET'. The rest will involve some heavy lifting with physical files

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest

# Setting up path for API source
import sys, os, json
sys.path.append("api")

import crudAPI
import httpStatusCodes

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
            bodyContent = request.POST
            stringifyedContent =dict((str(k), str(v)) for k,v in bodyContent.items())
            stringifyedContent['size'] = request.FILES['blob'].size
            print('size of file', request.FILES['blob'].size)
            createdFile = uploader.models.Blob(
                    content=request.FILES['blob'], **stringifyedContent)

            print('createdFile', createdFile)
            response = HttpResponse()
            try:
                createdFile.save()
                response.status_code = 200
                response.status_message = 'Successful upload'
            except Exception, e:
                print('exception', e)
                response.status_code = httpStatusCodes.INTERNAL_SERVER_ERROR
                response.status_message = 'Exception during uploading'

            return response
    elif request.method == 'PUT':
        # TODO: Match up the query and update keys with those in the API
        response = HttpResponse()
        try:
            queryBody = request.GET
            updateBody = request.POST

            if not queryBody:
                response.write(json.dumps(
                    dict(count=0, msg='Specify at least one identifier')
                ))
                response.status_code = httpStatusCodes.BAD_REQUEST
            elif uploader.models.Blob.objects.count() < 1:
                response.write(json.dumps(
                    dict(count=0, msg='No objects present yet')
                ))
                response.status_code = httpStatusCodes.NOT_FOUND
            else:
                # Use first element to sample what attributes are allowed to be updated
                mappedValues = crudAPI.captureOnlyAllowedAttrsFromObj(
                    uploader.models.Blob.objects.first(), queryBody
                )

                matchedQuerySet = uploader.models.Blob.objects.filter(*mappedValues)
                if not matchedQuerySet:
                    response.status_code = httpStatusCodes.NOT_FOUND
                else:
                    if request.FILES:
                        blob = request.FILES.get('blob', None)
                        if blob is not None:
                            updateBody['content'] = blob

                    matchedQuerySet.update(**updateBody)

                response.write(json.dumps(dict(count=matchedQuerySet.count())))
                
        except Exception, e:
            print(e, 'here')
            response.status_code = httpStatusCodes.INTERNAL_SERVER_ERROR
            response.status_message = str(e)

        finally:
            return response
    elif request.method == 'DELETE':
        response = HttpResponse()
        try:
            queryBody = request.GET # TODO: Enforce param passing in through .read()
            fromUnicodeConv = dict((str(k), str(v)) for k,v in queryBody.items())
            print('fromUC', fromUnicodeConv)
            matchedQuerySet = uploader.models.Blob.objects.filter(**fromUnicodeConv)
            print('matchedQuerySet', matchedQuerySet)
            
            if matchedQuerySet:
                successful, failed = [], []
                count = matchedQuerySet.count()
                for item in matchedQuerySet:
                    try:
                        os.unlink(item.content.path)
                    except Exception, e:
                        failed.append((item.id, item.title, item.size, str(e),)) 
                    else:
                        successful.append((item.id, item.title, item.size,))

                matchedQuerySet.delete()
                response.write(
                    json.dumps(dict(count=count, successful=successful, failed=failed))
                )

        except Exception, e:
            print('e', e)
            response.status_code = httpStatusCodes.INTERNAL_SERVER_ERROR
            response.status_message = str(e)

        return response
    else:
        # Only 'GET' will have access to the serialized content
        return crudAPI.handleHTTPRequest(
            request, uploaderConstants.BLOB_TABLE_KEY, uploader.models
        )
