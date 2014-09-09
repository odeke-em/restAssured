# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Module to help with authentication

import json
import hashlib
from django.http import HttpResponse
import django.contrib.auth as djangoAuth
from django.views.decorators.csrf import csrf_exempt

# Setting up path for API source
import sys, os
sys.path.append("api")
import crudAPI
import httpStatusCodes

import auth.models as authModels
import auth.authConstants as authConstants

byteFyArgs = {}
pyVersion = sys.hexversion//(1<<24)

if pyVersion >= 3:
    byteFyArgs = {'encoding': 'utf-8'}

hashAlgoMemoizer = {}

def getHash(obj, hashAlgoName='sha256'):
    if not obj:
        return httpStatusCodes.BAD_REQUEST, None

    hashAlgo = hashAlgoMemoizer.get(hashAlgoName, None)
    if not hashAlgo: # Cache miss
        hashAlgo = getattr(hashlib, hashAlgoName, None)
        if not hashAlgo:
            return httpStatusCodes.METHOD_NOT_ALLOWED, None

        hashAlgoMemoizer[hashAlgoName] = hashAlgo # Now memoized

    if not isinstance(obj, bytes):
        if not hasattr(obj, '__str__'): 
            return httpStatusCodes.METHOD_NOT_ALLOWED, None

        # Mutate it and bytefy it
        obj = bytes(str(obj), **byteFyArgs)

    return httpStatusCodes.OK, hashAlgo(obj).hexdigest()
   
def requiredHttpMethodCheck(request, methodName):
    method = request.method
    if method != methodName:
        resp = HttpResponse()
        resp.status_code = httpStatusCodes.METHOD_NOT_ALLOWED
        resp.write(json.dumps({'msg': 'Only %s method allowed'%(methodName)}))
        return resp

def credentialFieldCheck(
    credentials, expectedFields=['app_id', 'username', 'password']
):
    for keyword in expectedFields:
        retr = credentials.get(keyword, None)
        if not retr:
            response = HttpResponse()
            response.write(json.dumps({'msg': 'Expecting: %s'%(keyword)}))
            response.status_code = httpStatusCodes.BAD_REQUEST
            return response

def altParseRequestBody(request, methodName):
    reqBody = getattr(request, methodName, None)
    if not reqBody:
        try:
            reqBody = json.loads(
                request.read() if pyVersion < 3 else request.read().decode()
            )
        except Exception, e:
            return httpStatusCodes.INTERNAL_SERVER_ERROR, e

    return httpStatusCodes.OK, reqBody

@csrf_exempt
def newUser(request):
    notMethodCheckResponse = requiredHttpMethodCheck(request, 'POST')
    if notMethodCheckResponse:
        return notMethodCheckResponse

    missingCredsResponse = credentialFieldCheck(request.POST)
    if missingCredsResponse:
        return missingCredsResponse

    status, reqBody = altParseRequestBody(request, 'POST')
    if status != httpStatusCodes.OK:
        resp = HttpResponse()
        resp.status_code = httpStatusCodes.BAD_REQUEST
        resp.write(json.dumps({'msg': 'Could not create user. Try again later!'}))

    djangoUser = djangoAuth.authenticate(
        username=reqBody['username'], password=reqBody['password']
    )

    resp = HttpResponse()
    if not djangoUser:
        status, user = createDjangoUser(reqBody)
        if status != httpStatusCodes.OK:
            resp.status_code = httpStatusCodes.BAD_REQUEST
            return resp
    else:
        user = djangoUser

    appId = reqBody['app_id']
    authUserQuery = authModels.AuthUser.objects.filter(
        djangoUser_id=user.id, app_id=appId
    )

    response = HttpResponse()
    if authUserQuery:
        response.status_code = httpStatusCodes.CONFLICT
        response.write(json.dumps({'msg': 'User already exists'}))
    else:
        try:
            newAuthEntry = authModels.AuthUser(
                djangoUser_id=user.id, app_id=appId, meta=reqBody.get('meta', '')
            )
            newAuthEntry.save()
        except Exception, e:
            print(e)
            response.status_code = httpStatusCodes.BAD_REQUEST
            response.write(json.dumps({'msg': 'Failed to create user. Try again later'}))
        else:
            response.status_code = httpStatusCodes.OK
            response.write(json.dumps({'msg': 'User successfully created'}))

    return response

def createDjangoUser(userCredentials):
    # Allowed attributes
    allowedAttrs = ['password', 'first_name', 'email', 'username']
    createdB = {}
    for pickedKey in allowedAttrs:
        createdB[pickedKey] = userCredentials.get(pickedKey, '')

    try:
        freshUser = djangoAuth.models.User.objects.create_user(**createdB)
    except Exception, e:
        return httpStatusCodes.INTERNAL_SERVER_ERROR, e
    else:
        return httpStatusCodes.OK, freshUser

def login(request):
    notMethodCheckResponse = requiredHttpMethodCheck(request, 'GET')
    if notMethodCheckResponse:
        return notMethodCheckResponse
    
    credentials = request.GET

    missingCredsResponse = credentialFieldCheck(credentials, ['accessId', 'username', 'password'])
    if missingCredsResponse:
        return missingCredsResponse

    response = HttpResponse()
    appLookUp = authModels.App.objects.filter(_accessId=credentials['accessId'])
    if not appLookUp:
        response.status_code = 404
        response.write(json.dumps({'msg': 'No such app exists'}))
        return response

    # First step is logging them out
    logout(request)

    authedUser = djangoAuth.authenticate(
        username=credentials['username'], password=credentials['password']
    )

    if not authedUser:
        response.status_code = 404
        response.write(json.dumps({'msg': 'No such user found'}))
        return response

    appUserMatch = authModels.AuthUser.objects.filter(
        djangoUser_id=authedUser.id, app_id=appLookUp[0].id
    )
    if not appUserMatch:
        response.status_code = 404
        response.write(json.dumps({'msg': 'No such user found'}))
        return response

    # Final authentication now
    try:
        djangoAuth.login(request, authedUser)
    except Exception, e:
        print(e)
        response.status_code = httpStatusCodes.BAD_REQUEST
    else:
        response.status_code = httpStatusCodes.OK
        response.write(json.dumps({'msg': 'Success logging in'})) 

    return response

def logout(request):
    successfulLogout = False
    if request.user.is_authenticated():
        request.user.logout()
        successfulLogout = True

    response = HttpResponse()
    response.write(json.dumps({'successfulLogout': successfulLogout}))
        
    return response

@csrf_exempt
def appHandler(request):
    return crudAPI.handleHTTPRequest( 
        request, authConstants.APP_TABLE_KEY, authModels
    )
