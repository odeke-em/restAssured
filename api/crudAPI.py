#!/usr/bin/python
#
# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Copyright (c) 2014
# API to handle CRUD for any app whose models have been defined

import re
import sys
import json
import time
import inspect
import datetime
from django.http import HttpResponse

import httpStatusCodes
import globalVariables as globVars
import validatorFunctions as vFuncs

# Set to False during deployment
DEVELOPER_MODE = True

isCallable = lambda a: hasattr(a, '__call__')
isCallableAttr = lambda obj, attr:\
        hasattr(obj, attr) and isCallable(getattr(obj, attr))

isImmutableAttr = lambda s: s.startswith('_') or s in onlyServerCanWrite
isMutableAttr   = lambda s: not isImmutableAttr(s)

setSuffixCompile = re.compile(globVars.SET_SUFFIX_RE, re.UNICODE)
__TABLE_CACHE__ = dict()

# Dict to detect elements that by default are non json-serializable 
# but whose converters make them json-serializable
trivialSerialzdDict = {
  lambda e: e is None: lambda e: "null",
  lambda s: hasattr(s, globVars.NUMERICAL_DIV_ATTR): str,
  lambda s: isinstance(s, datetime.date) : lambda s: str(s.strftime('%s')),
}

tableDefinitions = dict()

# Attributes that are only modified by the server-side
# system and not by entries from the client side
onlyServerCanWrite = [
  globVars.ID_KEY, globVars.DATE_CREATED_KEY, globVars.LAST_EDIT_TIME_KEY
]

sortKeyCompile = re.compile(
    r"([^\s]*)\s*%s$"%(globVars.REVERSE_KEY), re.UNICODE|re.IGNORECASE
)

pyVersion = sys.version_info.major

if pyVersion >= 3:
  byteFyArgs = {'encoding': 'utf-8'}
else:
  byteFyArgs = {}

byteFy = lambda byteableObj: bytes(byteableObj, **byteFyArgs)

def translateSortKey(sortKey):
  if not sortKey:
    # If no sort parameter is passed in, sort by the newest reverse id
    # Returns: sortKey, ReverseTrueBoolean
    return globVars.ID_KEY, True
  
  # Let's get those reverse keys
  sortKeySearch = sortKeyCompile.search(sortKey)

  if sortKeySearch:
    return sortKeySearch.groups(1)[0], True
  else:
    return sortKey, False
 
def attemptJSONParse(strContent):
  outCode = httpStatusCodes.BAD_REQUEST
  deserial = None
  try:
    deserial = json.loads(strContent)
  except Exception as e:
    deserial = e
    outCode = httpStatusCodes.INTERNAL_SERVER_ERROR
  else:
    outCode = httpStatusCodes.OK
  finally:
    return outCode, deserial

def _altParseRequestBody(request, methodName, mustHaveContent=False):
  if not mustHaveContent:
    mustHaveContent = methodName == globVars.POST_KEY

  if methodName != globVars.PUT_KEY:
    reqBody = getattr(request, methodName, None)
  else:
    reqBody = request.GET
    qParams = reqBody.get('queryParams', '{}')
    uBody = reqBody.get('updateParams', '{}')
    try:
      updateParams = json.loads(uBody)
      queryParams = json.loads(qParams)
    except Exception, e:
      print('PUT EXCEPTION', e)
      reqBody = None
    else:
      reqBody = dict(queryParams=queryParams, updateParams=updateParams)

  if not reqBody:
      if reqBody is None or mustHaveContent:
        data = request.read() if pyVersion < 3 else request.read().decode()
        if not data: # Last resort
          reqBody = request.GET
        else:
          status, deserialized = attemptJSONParse(data)
          if status == httpStatusCodes.OK:
            reqBody = deserialized
          else:
            return status, deserialized

  return httpStatusCodes.OK, reqBody
 
def isSerializable(pyObj):
  # Elements serializable by default allow an iterator to be created from them
  try: iter(pyObj)
  except: return False
  else: return True

def getTablesInModels(models):
  # Returns a dict mapping table names to their objects,
  # for every table defined in models.py
  tableNameToTypeDict = __TABLE_CACHE__.get(models, None)
  if tableNameToTypeDict is None: # Cache miss here
     tableNameToTypeDict = dict()
     for elem in inspect.getmembers(models, inspect.isclass):
        name, obj = elem 
        tableNameToTypeDict[name] = obj
     __TABLE_CACHE__[models] = tableNameToTypeDict # Memoize it

  return tableNameToTypeDict

def captureUserMutableAttrsFromObj(samplerObj, mapUnderInspection):
  return captureUserMutableAttrs(getUserMutableFilters(samplerObj), mapUnderInspection)

def captureUserMutableAttrs(objEditableAttrs, mapUnderInspection):
  if not isCallableAttr(mapUnderInspection, '__getitem__'):
    raise Exception('Map under inspection must have __getitem__ or support [...] method')

  mappedValues = tuple()
  for key in objEditableAttrs:
    retrV = mapUnderInspection.get(key, None)
    if retrV is not None:
      mappedValues += ((key, retrV,),)

  return mappedValues

def getTableObjByKey(tableKeyName, models=None):
  # Returns the table object given the tableKeyName(a string)
  # if it is exists in the DB, else None
  if not tableKeyName:
    return None
  else:
    tablesInDB = getTablesInModels(models)
    return tablesInDB.get(tableKeyName, None)

def getSerializableElems(pyObj, salvageConverters=trivialSerialzdDict):
  # Returns the elements of an object that are json serializable
  if not pyObj:
    return {}

  if hasattr(pyObj, '__dict__'):
    dictRepr = pyObj.__dict__
  else:
    dictRepr = pyObj
    
  objDict = {}

  for key, value in dictRepr.items():
    if isSerializable(value):
      objDict[key] = value
    else: # Try for the non-serializable elements whose converters can be found
      serializedValue = passBasedOffFunc(value, salvageConverters)
      if serializedValue:
         objDict[key] = serializedValue

  return objDict

def passBasedOffFunc(value, salvageConverters):
  if not salvageConverters:
    return False
  for quantifier, converter in salvageConverters.items():
    if inspect.isfunction(quantifier) and quantifier(value):
      # Let's get the converted value and test for serializability
      converted = converter(value)
      if isSerializable(converted): return converted 

def suffixStrip(key, suffix):
  if not (key and suffix): return None

  beforeSuffixSearch = re.search("(.*)%s"%(suffix), key)
  if not beforeSuffixSearch: return None

  return beforeSuffixSearch.groups(1)[0]

def matchTable(tableKey, models):
  allTables = getTablesInModels(models)
  for key in allTables:
    if re.search("^%s$"%(tableKey), key, re.IGNORECASE): 
      return allTables.get(key)

def getForeignKeys(queryTable):
  return filter(
    lambda attr:attr.endswith(globVars.ID_SUFFIX), queryTable
  )

def getForeignKeyElems(pyObj, parentMap={}, models=None):
  if not pyObj:
    return None

  if pyObj.__hash__:
    hashOfObj = hash(pyObj)
    if hashOfObj in parentMap:
        return None

    # Memoize it now
    parentMap[hashOfObj] = hashOfObj

  foreignKeys = getForeignKeys(
    pyObj.__dict__ if hasattr(pyObj, '__dict__') else pyObj
  )

  if not foreignKeys: return None

  dataDict = dict()
  for foreignKey in foreignKeys:
    foreignId = getattr(pyObj, foreignKey, None)
    if not foreignId: continue # Corrupted data detected

    tableName = suffixStrip(foreignKey, globVars.ID_SUFFIX)
    tablePrototype = matchTable(tableName, models=None)
    if not tablePrototype: continue

    connObjs = tablePrototype.objects.filter((globVars.ID_KEY, foreignId))
    if not connObjs: continue

    connObj = connObjs[0]

    # Checking for self/cyclic reference
    if connObj.__hash__ and (hash(connObj) in parentMap):
       continue

    serializdDict = getSerializableElems(connObj)
    dataDict[tableName] = serializdDict

  return dataDict

def getConnectedElems(pyObj, alreadyVisited, models):
  # Return all table instances in which the current 'pyObj' is a foreign
  # key. These can normally be accessed by the table names in 
  #  lower_case <with> _set suffixed, eg pyObj.comment_set
  if not pyObj:
     return None

  objsets = [attr for attr in dir(pyObj) if setSuffixCompile.search(attr)]

  setElemsDict = dict()
  for objset in objsets:
    connElems = getattr(pyObj, objset, None)

    if not isCallableAttr(connElems, 'all'): # Or handle this miss as an err
       continue

    objList = list()
    for connElem in connElems.all():
      serializDict = getSerializableElems(connElem)
      if not serializDict:
        continue

      objHash = hash(pyObj)
      if objHash in alreadyVisited:
        # TODO: Show the cyclic dependency by
        # passing back a serializable sentinel
        continue

      alreadyVisited[objHash] = objHash

      connConnElems = getForeignKeyElems(connElem, alreadyVisited, models) 
      refObjs = getConnectedElems(connElem, alreadyVisited, models)

      if refObjs:
        serializDict.update(refObjs)

      if connConnElems:
        serializDict.update(connConnElems)

      objList.append(serializDict)

    setElemsDict[objset] = objList
    
  return setElemsDict 

def getTableByKey(tableName, models):
  if tableName:
    tables = getTablesInModels(models)
    return tables.get(tableName, None)

def updateTable(tableObj, bodyFromRequest, updateBool=False):
  # This is to handle the CREATE and UPDATE methods of CRUD
  # Args:
  #  tableObj => ProtoType of the table to be updated
  #  bodyFromRequest => {
  #    updateParams => A dict containing the fields to be changed in the table,
  #    queryParams => A dict containing the tables to query
  #  }
  #  updateBool  => Set to False, means that you are creating an entry,
  #                 True, means an update 
  #  Note:  If updateBool is set, you MUST provide an 'id' in 'updateParams'
  if not (tableObj and bodyFromRequest): 
    return None # Handle this mishap later

  errorID = -1 
  changeCount = duplicatesCount = 0
  if not isinstance(bodyFromRequest, dict):
    print("Arg 2 must be a dictionary")
    return errorID, changeCount, duplicatesCount

  allowedKeys = None
  if not updateBool:
    objectToChange = tableObj()
    updateParams = bodyFromRequest
    allowedKeys = getUserMutableFilters(objectToChange)

  else:
    queryParams = bodyFromRequest.get('queryParams', None)
    if not isinstance(queryParams, dict):
      print('Expecting a query body passed in as a dict')
      return errorID, changeCount, duplicatesCount

    elif tableObj.objects.count() < 1: # Journey cut short if not even a single item exists
      return errorID, changeCount, duplicatesCount

    else:
      allowedFilters = captureUserMutableAttrsFromObj(
                                tableObj.objects.first(), queryParams)

      objMatch = tableObj.objects.filter(*allowedFilters)

      if not objMatch:
        print(
           'Error: Could not find items that match query params', queryParams)
        return errorID, changeCount, duplicatesCount
      else:
        allowedKeys = getUserMutableFilters(objMatch[0])
        if objMatch.count() == 1: # Just one item can be individually inspected
            objectToChange = objMatch[0]
        else:
            objectToChange = objMatch

        updateParams = bodyFromRequest.get('updateParams', None)
        if updateParams is None:
          updateParams = {}

  cherryPickedAttrs = dict(
    (str(k), updateParams[k]) for k in updateParams if isMutableAttr(k) and k in allowedKeys
  )

  if isCallableAttr(objectToChange, 'update'):
    objectToChange.update(**cherryPickedAttrs)
    changeCount = objectToChange.count()
    return changeCount, changeCount, -1
  else:
    for attr in cherryPickedAttrs:
       attr = str(attr) # To handle the initial unicode form eg u'key' yet desired is 'key'

       attrValue = updateParams.get(attr)
       if updateBool: 
          origValue = getattr(objectToChange, attr, None)
          if (attrValue == origValue): 
             duplicatesCount += 1
             continue

       setattr(objectToChange, attr, attrValue)
       changeCount += 1

    if not changeCount: 
      return objectToChange.id, changeCount, duplicatesCount
    else:
      # Let's get that data written to memory
      savedBoolean = saveToMemory(objectToChange)

      if savedBoolean:
        return objectToChange.id, changeCount, duplicatesCount
      else:
        return errorID, -1, -1

def deleteByAttrs(objProtoType, attrDict):
  # Given a table's name and the identifier attributes, attempt a deletion 
  # Returns: DELETION_FAILURE_CODE on any parameter errors
  #          DELETION_EXCEPTION_CODE on deletion error/exception
  #          DELETION_SUCCESS_CODE on successful deletion
  #   *** The above codes are defined in the globVars file ***

  if not objProtoType:
    msg = "No such table"
    print(msg, "Unknown table ", objProtoType)
    return dict(
        successful=[], failed=[], id=globVars.DELETION_FAILURE_CODE, msg=msg)
  elif not isinstance(attrDict, dict):
    msg = 'parameter \'attrDict\' must be an instance of a dict'
    print(msg)
    return dict(
        successful=[], failed=[], id=globVars.DELETION_FAILURE_CODE, msg=msg)

  else: 
    tupledIdentifiers = tuple(attrDict.items()) 
    matchedElems = objProtoType.objects.filter(*tupledIdentifiers)

    if not matchedElems:
      msg = "During delete could not find such elements"
      print(msg, tupledIdentifiers)
      return dict(successful=[], failed=[], msg=msg)
    else:
      failed, successful = [], []

      for elem in matchedElems:
        elemId = elem.id
        selector = failed

        try:
          elem.delete()
          selector = successful

        except Exception, ex:
          print(ex)

        finally:
          selector.append(elemId)

      return dict(successful=successful, failed=failed)

def saveToMemory(newObj):
  # Note: Invoking obj.save() returns None so we track a save
  #       success only if no exception is thrown 
  if not hasattr(newObj, 'save'): 
     return False

  savedBool = False
  try: 
    newObj.save()
  except Exception, ex:
    print(ex)
  else: 
    savedBool = True

  return savedBool

def handleHTTPRequest(request, tableName, models):
  startTime = time.time()

  requestMethod = request.method

  resultsDict = None
  response = HttpResponse()
  statusCode = httpStatusCodes.BAD_REQUEST

  parseStatus, content = _altParseRequestBody(request, requestMethod)

  if parseStatus != httpStatusCodes.OK:
    statusCode = httpStatusCodes.BAD_REQUEST  
    resultsDict = {'msg': 'No body could be parsed'}
  else:
    tableProtoType = getTableByKey(tableName, models)

    if requestMethod == globVars.GET_KEY:
      statusCode, resultsDict = handleGET(content, tableProtoType, models)

    elif requestMethod == globVars.POST_KEY:
      statusCode, resultsDict = handlePOST(content, tableProtoType)

    elif requestMethod == globVars.DELETE_KEY:
      statusCode, resultsDict = handleDELETE(content, tableProtoType)

    elif requestMethod == globVars.PUT_KEY:
      statusCode, resultsDict = handlePUT(content, tableProtoType)
 
    else:
      resultsDict = {'msg': 'Unknown method'}
      statusCode = httpStatusCodes.METHOD_NOT_ALLOWED

  addTypeInfo(resultsDict)
  response.status_code = statusCode
  resultsDict['timeCost'] = time.time() - startTime

  response.write(json.dumps(resultsDict))

  return response

def getUserMutableFilters(tableProtoType):
  if not tableProtoType:
    return None
  else:
    userDefFields = __TABLE_CACHE__.get(tableProtoType, None)

    if userDefFields is None:
      objDict = tableProtoType.__dict__

      userDefFields = tuple(attr for attr in objDict if isMutableAttr(attr))
      __TABLE_CACHE__[tableProtoType] = userDefFields

    return userDefFields

def addTypeInfo(outDict):
  if isinstance(outDict, dict):
    outDict["dataType"] = "json"
    outDict["mimeType"] = "application/json"
    outDict["currentTime"] = getCurrentTime()

def getCurrentTime():
  return time.time()

################################# CRUD handlers below ################################
def handlePUT(putBody, tableProtoType):
  results = updateTable(
      tableProtoType, bodyFromRequest=putBody, updateBool=True
  )

  if results:
    changedID, changeCount, duplicatesCount = results

    return httpStatusCodes.OK, dict(
        id=changedID, changeCount=changeCount, duplicatesCount=duplicatesCount
    )
  else:
    return httpStatusCodes.BAD_REQUEST, dict(id=-1)

def handleGET(getBody, tableObj, models=None):
  if not tableObj:
    print("No results")
    return httpStatusCodes.NOT_FOUND, {'msg': "I need a table prototype"}

  tableObjManager = tableObj.objects
  objCount = tableObjManager.count()

  #========================= Population and Filtration here ========================#
  objProto = tableObj()
  bodyAttrs = getUserMutableFilters(objProto)

  dbObjs = tableObjManager
  nFiltrations = 0

  allowedFilters = captureUserMutableAttrs(bodyAttrs, getBody)

  # Finally we should also capture the id
  if 'id' in getBody:
    cId = None
    rId = getBody['id']
    if vFuncs.isUIntLike(rId):
      cId = rId
    elif type(rId) == 'list' and len(rId): # Query dicts trip out by providing u'id': [i]
      cId = rId[0]

    if cId is not None:
      allowedFilters += (('id', int(cId)),)

  selectAttrs = getBody.get(globVars.SELECT_KEY, None)
  selectKeys = None
  if selectAttrs:
    splitKeys = selectAttrs.split(',')
    # Always want id's
    if globVars.ID_KEY not in splitKeys:
      splitKeys.append(globVars.ID_KEY) 

    # Then convert to a tuple to allow dereferencing/unravelling of elements
    selectKeys = tuple(key for key in splitKeys if key in bodyAttrs)

    bodyAttrs = selectKeys

    # Populate only the requested attributes
    dbObjs = dbObjs.values(*selectKeys).all() if not allowedFilters\
                        else dbObjs.values(*selectKeys).filter(*allowedFilters)
  else:
    dbObjs = dbObjs.filter(*allowedFilters)

  #=================================================================================#
 
  #========================== Pagination and OffSets here ==========================#
  limit = getBody.get(globVars.LIMIT_KEY, None)

  if limit is None: 
    limit=0
  elif not vFuncs.isUIntLike(limit): # Only postive limits accepted
    limit = globVars.THRESHOLD_LIMIT
  else:  
    limit = int(limit)
  
  offSet = getBody.get(globVars.OFFSET_KEY, None)

  # Only accept positive offsets
  if not (offSet and vFuncs.isUIntLike(offSet)):
    offSet = globVars.THRESHOLD_OFFSET
  else:
    offSet = int(offSet)
 
  maxSize = dbObjs.count()
  if limit > maxSize:
    limit = maxSize 
  elif limit:
    limit += offSet

  #=============================== SORTING HERE ===================================#
  sortKey = getBody.get(globVars.SORT_KEY, None)
  sortKey, reverseTrue = translateSortKey(sortKey)
  if sortKey not in bodyAttrs: 
     sortKey = "-%s"%(globVars.ID_KEY)

  elif reverseTrue: 
     sortKey = "-%s"%(sortKey)
  
  #================================================================================#

  #============================== FORMAT HERE =====================================#
  formatKey = getBody.get(globVars.FORMAT_KEY, globVars.LONG_FMT_KEY)

  # Defining the default behaviour of the API to always return results
  # of 'long' as long format 'short' hasn't been defined
  # format=xong or format=zrer, should be interpreted as format=long
  connectedObjsBool = \
      re.search(formatKey, globVars.SHORT_FMT_KEY) == None

  data = list()

  if not limit:
    dbObjIterator = dbObjs.order_by(sortKey)[offSet:]
  else:
    dbObjIterator = dbObjs.order_by(sortKey)[offSet:limit]

  foreignVisited = {}
  connectedVisited = {}
  idMap = {}
  for dbObj in dbObjIterator:
    connmap = {}
    foreignKeyElems = getForeignKeyElems(dbObj, foreignVisited, models=models)
    if foreignKeyElems:
      connmap.update(foreignKeyElems)
    
    if connectedObjsBool: # A join requested
      connElems = getConnectedElems(dbObj, connectedVisited, models)
      if connElems:
        connmap.update(connElems)

    if hasattr(dbObj, 'id'):
      itemId = dbObj.id
    else:
      itemId = dbObj.get('id', None)
      if itemId is None:
        continue

    idMap[itemId] = connmap

  qs = dbObjIterator.values('id', *bodyAttrs)
  for item in qs:
     itId = item.get('id', -1)
     retrObj = idMap.get(itId, {})
     if retrObj:
       item.update(retrObj)

  data = [getSerializableElems(qi) for qi in qs]
  metaDict = dict(
    collectionCount=objCount, count=len(data),
    format=formatKey,sort=sortKey, limit=limit, offset=offSet
  )

  if selectKeys:
    metaDict[globVars.SELECT_KEY] = selectKeys

  return httpStatusCodes.OK, dict(meta=metaDict, data=data)

def handlePOST(postBody, tableProtoType):
  statusCode = httpStatusCodes.BAD_REQUEST
  results = updateTable(
    tableProtoType, bodyFromRequest=postBody, updateBool=False
  )

  resultsDict = dict()

  if results:
    changedID, changeCount, duplicatesCount = results
    resultsDict = {
      'data': {
        'id':changedID, 'changeCount': changeCount, 'duplicatesCount': duplicatesCount
      }
    }
    statusCode = httpStatusCodes.OK

  return statusCode, resultsDict

def handleDELETE(deleteBody, tableProtoType):
  return httpStatusCodes.OK, dict(data=deleteByAttrs(tableProtoType, deleteBody))
