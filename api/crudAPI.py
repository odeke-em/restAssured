#!/usr/bin/python
#
# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Copyright (c) 2014
# API to handle CRUD for any app whose models have been defined

import re
import json
import time
import copy
import inspect
from django.http import HttpResponse
from django.shortcuts import render_to_response

import datetime

import httpStatusCodes
import validatorFunctions as vFuncs
import globalVariables as globVars

# Set to False during deployment
DEVELOPER_MODE = True

isCallable = lambda a: hasattr(a, '__call__')
isCallableAttr = lambda obj,attr: hasattr(obj, attr) and isCallable(getattr(obj, attr))

isImmutableAttr = lambda s: s.startswith('_') or s in onlyServerCanWrite
isMutableAttr   = lambda s: not isImmutableAttr(s)

setSuffixCompile = re.compile(globVars.SET_SUFFIX_RE, re.UNICODE)
__TABLE_CACHE__ = dict()

# Dict to detect elements that by default are non json-serializable 
# but whose converters make them json-serializable
trivialSerialzdDict = {
  lambda e: e is None: lambda e: "null",
  lambda s: hasattr(s, globVars.NUMERICAL_DIV_ATTR): str,
  lambda s: isinstance(s, datetime.date) : lambda s: str(s.strftime('%s'))
}

tableDefinitions = dict()

# Attributes that are only modified by the server-side
# system and not by entries from the client side
onlyServerCanWrite = [
  globVars.ID_KEY, globVars.DATE_CREATED_KEY, globVars.LAST_EDIT_TIME_KEY
]

sortKeyCompile = re.compile(r"([^\s]*)\s*%s$"%(globVars.REVERSE_KEY), re.UNICODE|re.IGNORECASE)

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
    return dict()

  # First create a copy of the object's attributes 
  getid = None
  dictRepr = None
  if hasattr(pyObj, '__dict__'):
    getid = lambda : pyObj.__getattribute__(globVars.ID_KEY)
    dictRepr = pyObj.__dict__
  else:
    getid = lambda : pyObj.get(globVars.ID_KEY, None)
    dictRepr = pyObj
    
  objDict = copy.copy(dictRepr)

  nonSerializbleElems = filter(
    lambda attrValueTuple:not isSerializable(attrValueTuple[1]),\
    objDict.items()
  )

  # Non-serializable elements whose converters can be found
  salvagableElems = list()

  for attr, value in nonSerializbleElems:
    serialValue = passBasedOffFunc(value, salvageConverters)
    if not serialValue:
       objDict.pop(attr)
    else:
      salvagableElems.append((attr, serialValue))

  for elem in salvagableElems:
    key, value = elem[0], elem[1]
    objDict[key] = value

  objDict[globVars.ID_KEY] = getid()

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

  hashOfObj = hash(pyObj)
  if hashOfObj in parentMap:
    print('\033[47mAlready memoized %d\033[00m'%(pyObj.id))
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

    if (hash(connObj) in parentMap): # Detected self/cyclic reference
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
      if not serializDict: continue

      if pyObj not in alreadyVisited:
        objHash = hash(pyObj) # No need to memoize the object, its hash will do
        alreadyVisited[objHash] = objHash
        # print('Memoizing', pyObj.id)

      connConnElems = getForeignKeyElems(connElem, alreadyVisited, models) 
      refObjs = getConnectedElems(connElem, alreadyVisited, models)

      mergeDicts(connConnElems, serializDict)
      mergeDicts(refObjs, serializDict)

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
  #  updatesBody => A dict containing the fields to be changed in the table
  #  updateBool  => Set to False, means that you are creating an entry,
  #                 True, means an update 
  #  Note:  If updateBool is set, you MUST provide an 'id' in 'updatesBody'
  if not (tableObj and bodyFromRequest): 
    return dict() # Handle this mishap later

  errorID = -1 
  changecount = duplicatescount = 0
  if not isinstance(bodyFromRequest, dict):
    print("Arg 2 must be a dictionary")
    return errorID, changecount, duplicatescount

  allowedKeys = None
  if not updateBool:
    objectToChange = tableObj()
    updatesBody = bodyFromRequest
    allowedKeys = getAllowedFilters(objectToChange)

  else:
    queryParams = bodyFromRequest.get('queryParams', None)
    if not isinstance(queryParams, dict):
      print('Expecting a query body passed in as a dict')
      return errorID, changecount, duplicatescount

    else:
      objMatch = tableObj.objects.filter(**queryParams)
      if not objMatch:
        print('Error: Could not find items that match query params', queryParams)
        return errorID, changecount, duplicatescount
      else:
        allowedKeys = getAllowedFilters(objMatch[0])
        if objMatch.count() == 1: # Just one item can be individually inspected
            objectToChange = objMatch[0]
        else:
            objectToChange = objMatch

        updatesBody = bodyFromRequest.get('updatesBody', None)
        if updatesBody is None:
          updatesBody = {}

  cherryPickedAttrs = dict(
    (str(k), updatesBody[k]) for k in updatesBody if isMutableAttr(k) and k in allowedKeys
  )

  if isCallableAttr(objectToChange, 'update'):
    objectToChange.update(**cherryPickedAttrs)
    changeCount = objectToChange.count()
    return changeCount, changeCount, -1
  else:
    for attr in cherryPickedAttrs:
       attr = str(attr) # To handle the initial unicode form eg u'key' yet desired is 'key'

       attrValue = updatesBody.get(attr)
       if updateBool: 
          origValue = getattr(objectToChange, attr, None)
          if (attrValue == origValue): 
             duplicatescount += 1
             continue

       setattr(objectToChange, attr, attrValue)
       changecount += 1

    if not changecount: 
      return objectToChange.id, changecount, duplicatescount
    else:
      # Let's get that data written to memory
      savedBoolean = saveToMemory(objectToChange)

      if savedBoolean:
        return objectToChange.id, changecount, duplicatescount
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
    return dict(successful=[], failed=[], id=globVars.DELETION_FAILURE_CODE, msg=msg)
  elif not isinstance(attrDict, dict):
    msg = 'parameter \'attrDict\' must be an instance of a dict'
    print(msg)
    return dict(successful=[], failed=[], id=globVars.DELETION_FAILURE_CODE, msg=msg)

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
  requestMethod = request.method

  tableProtoType = getTableByKey(tableName, models)

  if requestMethod == globVars.GET_KEY:
    getBody = request.GET
    return handleGET(getBody, tableProtoType, models)

  elif requestMethod == globVars.POST_KEY:
    postBody = request.POST
    if not postBody:
      try:
        loaded = json.loads(request.read())
      except Exception, ex:
        print(ex)
      else:
        postBody = loaded 

    return handlePOST(postBody, tableProtoType)

  elif requestMethod == globVars.DELETE_KEY:
    return handleDELETE(request, tableProtoType)

  elif requestMethod == globVars.PUT_KEY:
    return handlePUT(request, tableProtoType)
 
  else:
    errorResponse = HttpResponse("Unknown method") 
    errorResponse.status_code = httpStatusCodes.METHOD_NOT_ALLOWED
  
    return errorResponse

def getAllowedFilters(tableProtoType):
  if not tableProtoType:
    return None
  else:
    userDefFields = __TABLE_CACHE__.get(tableProtoType, None)

    if userDefFields is None:
      objDict = tableProtoType.__dict__
      userDefFields = [attr for attr in objDict if not attr.startswith('_')]
      __TABLE_CACHE__[tableProtoType] = userDefFields

    return userDefFields

def mergeDicts(src, dest):
  if hasattr(src, 'items') and hasattr(dest, '__setitem__'):
    for srcKey, srcValue in src.items():
      dest[srcKey] = srcValue

def addTypeInfo(outDict):
  if isinstance(outDict, dict):
    outDict["dataType"] = "json"
    outDict["mimeType"] = "application/json"
    outDict["currentTime"] = getCurrentTime()

def getCurrentTime():
  return time.time()

################################# CRUD handlers below ################################
def handlePUT(request, tableProtoType):
  response = HttpResponse()

  try:
    body = request.read()
    putBody = json.loads(body)

  except Exception, ex:
    print(ex)

  else:
    results = updateTable(tableProtoType, bodyFromRequest=putBody, updateBool=True)

    if results:
      changedID, changecount, duplicatescount = results
      resultsDict = dict(
        id=changedID, changecount=changecount, duplicatescount=duplicatescount
      )
    else:
      resultsDict = dict(id=-1)

    response.write(json.dumps(resultsDict))

  return response

def handleGET(getBody, tableObj, models=None):
  response = HttpResponse()
  if not tableObj:
    response.status_code = 403
    response.status_message = "I need a table prototype"
    print("No results")
    return response

  tableObjManager = tableObj.objects
  objCount = tableObjManager.count()

  #================================ FILTRATION HERE ================================#
  objProto = tableObj()
  bodyAttrs = getAllowedFilters(objProto)

  dbObjs = tableObjManager
  nFiltrations = 0

  mappedValues = [(k, getBody.get(k, None)) for k in bodyAttrs]
  allowedFilters = filter(lambda e : e[1], mappedValues)

  selectAttrs = getBody.get(globVars.SELECT_KEY, None)
  selectKeys = None
  if selectAttrs:
    splitKeys = selectAttrs.split(',')
    # Always want id's
    if globVars.ID_KEY not in splitKeys:
      splitKeys.append(globVars.ID_KEY) 

    # Then convert to a tuple to allow dereferencing/unravelling of elements
    selectKeys = tuple([key for key in splitKeys if key in bodyAttrs])

    # Populate only the requested attributes
    dbObjs = dbObjs.values(*selectKeys).all() if not allowedFilters\
                else dbObjs.values(*selectKeys).filter(*allowedFilters)
  else:
    dbObjs = dbObjs.all() if not allowedFilters else dbObjs.filter(*allowedFilters)
  #=================================================================================#
 
  #========================== Pagination and OffSets here ==========================#
  limit = getBody.get(globVars.LIMIT_KEY, None)

  if limit is None: 
    limit=0
    # Only postive limits accepted
  elif not vFuncs.isUIntLike(limit):
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
  if limit > maxSize: limit = maxSize 
  elif limit: limit += offSet

  #=============================== SORTING HERE ===================================#
  sortKey = getBody.get(globVars.SORT_KEY, None)
  sortKey, reverseTrue = translateSortKey(sortKey)
  if sortKey not in bodyAttrs: 
     sortKey = "-%s"%(globVars.ID_KEY)

  elif reverseTrue: 
     sortKey = "-%s"%(sortKey)
  
  dbObjs = dbObjs.order_by(str(sortKey))

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

  alreadyVisited = {}
  for dbObj in dbObjIterator:
    dbElemDict = getSerializableElems(dbObj)
    foreignKeyElems = getForeignKeyElems(dbObj, alreadyVisited, models=models)
    if foreignKeyElems:  mergeDicts(foreignKeyElems, dbElemDict)
    
    if connectedObjsBool: # A join requested
      connElems = getConnectedElems(dbObj, alreadyVisited, models)
      if connElems:
        mergeDicts(connElems, dbElemDict)

    data.append(dbElemDict)

  metaDict = dict(
    count=objCount, format=formatKey,sort=sortKey, limit=limit, offset=offSet
  )

  if selectKeys:
    metaDict[globVars.SELECT_KEY] = selectKeys

  responseDict = dict(meta=metaDict, data=data)

  addTypeInfo(responseDict)
  response.write(json.dumps(responseDict))

  return response

def handlePOST(postBody, tableProtoType):
  response = HttpResponse()
  results = updateTable(
    tableProtoType, bodyFromRequest=postBody, updateBool=False
  )


  resultsDict = dict()

  if results:
    changedID, changecount, duplicatescount = results
    resultsDict =\
      dict(data=dict(id=changedID, changecount=changecount, duplicatescount=duplicatescount))
  else:
    response.status_code = httpStatusCodes.BAD_REQUEST  

  addTypeInfo(resultsDict)
  response.write(json.dumps(resultsDict))

  return response

def handleDELETE(request, tableProtoType):
  response = HttpResponse()

  try:
    body = request.read()
    deleteBody = json.loads(body)
  except Exception, ex:
    print(ex, 'During delete')
    response.satus_code = httpStatusCodes.INTERNAL_SERVER_ERROR
  else:
    resultsDict = dict(
        data=deleteByAttrs(tableProtoType, deleteBody)
    )

    addTypeInfo(resultsDict)
    response.write(json.dumps(resultsDict))

  return response
