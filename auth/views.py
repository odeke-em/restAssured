# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Module to help with authentication

import json
import hmac
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

byteFy = lambda byteableObj: bytes(byteableObj, **byteFyArgs)

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
        obj = byteFy(str(obj))

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

    status, reqBody = altParseRequestBody(request, 'POST')
    if status != httpStatusCodes.OK:
        resp = HttpResponse()
        resp.status_code = httpStatusCodes.BAD_REQUEST
        resp.write(json.dumps({'msg': 'Failed to parse content from the request. Try again later!'}))

    missingCredsResponse = credentialFieldCheck(reqBody, ['appAccessId', 'username'])
    if missingCredsResponse:
        return missingCredsResponse

    appAccessId = reqBody['appAccessId']
    appLookUp = authModels.App.objects.filter(_accessId=appAccessId)

    if not appLookUp:
        response.status_code = 404
        response.write(json.dumps({'msg': 'No such app exists'}))
        return response

    djangoUser = djangoAuth.models.User.objects.filter(username=reqBody['username'])

    resp = HttpResponse()
    if not djangoUser:
        status, user = createDjangoUser(reqBody)
        if status != httpStatusCodes.OK:
            resp.status_code = httpStatusCodes.BAD_REQUEST
            return resp
    else:
        user = djangoUser[0]

    authUserQuery = authModels.AuthUser.objects.filter(djangoUser_id=user.id, app_id=appLookUp[0].id)

    response = HttpResponse()
    if authUserQuery:
        response.status_code = httpStatusCodes.CONFLICT
        response.write(json.dumps({'msg': 'User already exists'}))
    else:
        try:
            newAuthEntry = authModels.AuthUser(
                djangoUser_id=user.id, app_id=appLookUp[0].id, meta=reqBody.get('meta', '')
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
    allowedAttrs = ['first_name', 'last_name', 'email', 'username']
    createdB = {}
    for pickedKey in allowedAttrs:
        createdB[pickedKey] = userCredentials.get(pickedKey, '')

    createdB['password'] = authModels.generateUUID().hex

    try:
        freshUser = djangoAuth.models.User.objects.create_user(**createdB)
    except Exception, e:
        return httpStatusCodes.INTERNAL_SERVER_ERROR, e
    else:
        return httpStatusCodes.OK, freshUser

def checkHMACValidity(userKey, msg, purportedResponse):
    return hmac.HMAC(key=userKey, msg=msg, digestmod=hashlib.sha256).hexdigest() == purportedResponse

def loginByPassword(request):
    '''
        This is the traditional login method
        Requires credentials:
            + appAccessId: The id provided to the app.
            + accessId: The id assigned to the user when they signed up to the app.
            + password: A non-empty string.
            + username: A non-empty string.
    '''
    notMethodCheckResponse = requiredHttpMethodCheck(request, 'POST')
    if notMethodCheckResponse:
        return notMethodCheckResponse
    
    credentials = altParseRequestBody(request, 'POST')

    missingCredsResponse = credentialFieldCheck(credentials, ['appAccessId', 'accessId', 'password', 'username'])
    if missingCredsResponse:
        return missingCredsResponse

    response = HttpResponse()
    appLookUp = authModels.App.objects.filter(_accessId=credentials['appAccessId'])

    if not appLookUp:
        response.status_code = 404
        response.write(json.dumps({'msg': 'No such app exists'}))
        return response

    # Log them out to begin with
    logout(request)

    djangoUser = djangoAuth.authenticate(username=credentials['username'], password=credentials['password'])
    if not djangoUser:
        response.status_code = 404
        response.write(json.dumps({'msg': 'Access denied. Check the provided credentials!'}))
        return response

    headApp = appLookUp[0]
    appUser = authModels.AuthUser.objects.filter(
        app_id=headApp._id, djangoUser_id=djangoUser._id, accessId=credentials['accessId']
    )

    if not appUser:
        response.status_code = 404
        response.write(json.dumps({'msg': 'Access denied. Check the provided credentials!'}))
        return response

    try:
        djangoAuth.login(request, djangoUser)
    except Exception, e:
        print(e)
        response.status_code = httpStatusCodes.BAD_REQUEST
    else:
        response.status_code = httpStatusCodes.OK
        response.write(json.dumps({'msg': 'Success logging in'})) 

    return response

def loginBySignature(request):
    '''
        Takes in a digest to be verified, that was purportedly obtained by signing with
        the user's private credentials on the client side. Verifies if the signatures match up
        Requires credentials:
            + appAccessId: The id provided to the app.
            + accessId: The id assigned to the user when they signed up to the app.
            + signature: The digest to be verified after signing with the user's private key.
        Note: Does not yet attach the user to the request since so far authenticate(...) requires
              password and username to be sent in, but this function doesn't even require usernames nor passwords
    '''
    notMethodCheckResponse = requiredHttpMethodCheck(request, 'POST')
    if notMethodCheckResponse:
        return notMethodCheckResponse
    
    credentials = altParseRequestBody(request, 'POST')

    missingCredsResponse = credentialFieldCheck(credentials, ['appAccessId', 'accessId', 'signature'])
    if missingCredsResponse:
        return missingCredsResponse

    response = HttpResponse()
    appLookUp = authModels.App.objects.filter(_accessId=credentials['appAccessId'])

    if not appLookUp:
        response.status_code = 404
        response.write(json.dumps({'msg': 'No such app exists'}))
        return response

    userAccessId = credentials['accessId']
    userLookUp = authModels.AuthUser.objects.filter(app_id=appLookUp[0].id, _accessId=userAccessId)
    if not userLookUp:
        response.status_code = 404
        response.write(json.dumps({'msg': 'Access denied. Check the accessId provided!'}))
        return response

    retrUser = userLookUp[0]

    djangoUserResults = djangoAuth.models.User.objects.filter(id=retrUser.djangoUser_id)
    if not djangoUserResults:
        response.status_code = 404
        response.write(json.dumps({'msg': 'Access denied. No such user exists'}))
        return response

    # Next step: Check out the validity of the hmac signature
    isValidSignature = checkHMACValidity(
        byteFy(retrUser._secretKey+userAccessId), credentials.get('message', ''), credentials['signature']
    )

    if not isValidSignature:
        print('\033[92mInvalid Signature\033[00m')
        response.status_code = httpStatusCodes.UNAUTHORIZED
        response.write(json.dumps({'msg': 'Purported response did not match our records'}))
        return response

    print('\033[92mIsValid Signature\033[00m')

    # TODO:  Associated the user with the request by .authenticate(**credentials)

    response.status_code = httpStatusCodes.OK
    response.write(json.dumps({'msg': 'Success logging in'})) 

    return response

def logout(request):
    '''
        Performs the reverse of logging in ie disassociates a user from the request, 
        but only if they are authenticated and associated to the incoming request.
    '''
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
