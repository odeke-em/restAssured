#!/usr/bin/python
#
# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Copyright (c) 2014
# API to handle CRUD for any app whose models have been defined

import re
import json
import inspect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse

import httpStatusCodes
import validatorFunctions as vFuncs
import globalVariables as globVars

# Set to False during deployment
DEVELOPER_MODE = True

# Dict to detect elements that by default are non json-serializable 
# but whose converters make them json-serializable
trivialSerialzdDict = {
  lambda e: e is None: lambda e:"null",
  lambda s: hasattr(s, globVars.NUMERICAL_DIV_ATTR): str
}

tableDefinitions = dict()

# Attributes that are only modified by the server-side
# system and not by entries from the client side
onlyServerCanWrite = [
  globVars.ID_KEY, globVars.SUBMISSION_DATE_KEY, globVars.LAST_TIME_EDIT_KEY
]

def translateSortKey(sortKey):
  if not sortKey:
    # If no sort parameter is passed in, sort by the newest reverse id
    # Returns: sortKey, ReverseTrueBoolean
    return globVars.ID_KEY, True
  
  # Let's get those reverse keys
  sortKeySearch = re.search(
    "([^\s]*)\s*%s$"%(globVars.REVERSE_KEY), sortKey, re.UNICODE|re.IGNORECASE
  )

  if sortKeySearch:
    return sortKeySearch.groups(1)[0], True
  else:
    return sortKey, False
  
def isSerializable(pyObj):
  # Elements serializable by default allow an iterator to be created from them
  try: iterator = iter(pyObj)
  except: return False
  else: return True

def getTablesInModels(models):
  # Returns a dict mapping table names to their objects,
  # for every table defined in models.py
  tableNameToTypeDict = dict()
  for classTuple in inspect.getmembers(models, inspect.isclass):
    name, obj = classTuple 
    tableNameToTypeDict[name] = obj

  return tableNameToTypeDict

def getTableObjByKey(tableKeyName, models=None):
  # Returns the table object given the tableKeyName(a string)
  # if it is exists in the DB, else None
  if not tableKeyName: return None
  tablesInDB = getTablesInModels(models)
  return tablesInDB.get(tableKeyName, None)

def getSerializableElems(pyObj, salvageConverters=trivialSerialzdDict):
  # Returns the elements of an object that are json serializable
  import copy
  if not pyObj: return dict()

  # First create a copy of the object's attributes 
  objDict = copy.copy(pyObj.__dict__)
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

  objDict[globVars.ID_KEY] = pyObj.__getattribute__(globVars.ID_KEY)

  return objDict

def passBasedOffFunc(value, salvageConverters):
  if not salvageConverters: return False
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
    lambda attr:attr.endswith(globVars.ID_SUFFIX), queryTable.__dict__
  )

def getForeignKeyElems(pyObj, callerTable=None):
  if not pyObj: return None
  elif callerTable is pyObj: return None

  foreignKeys = getForeignKeys(pyObj)
  if not foreignKeys: return None

  dataDict = dict()
  for foreignKey in foreignKeys:
    foreignId = pyObj.__getattribute__(foreignKey)
    if not foreignId: continue # Corrupted data detected

    tableName = suffixStrip(foreignKey, globVars.ID_SUFFIX)
    tablePrototype = matchTable(tableName)
    if not tablePrototype: continue

    connObjs = tablePrototype.objects.filter((globVars.ID_KEY, foreignId))
    if not connObjs: continue

    connObj = connObjs[0]

    # Detected self/cyclic reference
    if (callerTable == connObj): 
       continue

    serializdDict = getSerializableElems(connObj)
    dataDict[tableName] = serializdDict

  return dataDict

def getConnectedElems(pyObj):
  # Return all table instances in which the current 'pyObj' is a foreign
  # key. These can normally be accessed by the table names in 
  #  lower_case <with> _set suffixed, eg pyObj.comment_set
  if not pyObj: return None
  setSuffixCompile = re.compile(globVars.SET_SUFFIX_RE, re.UNICODE)
  objSets = filter(lambda attr:setSuffixCompile.search(attr), dir(pyObj))

  setElemsDict = dict()
  for objSet in objSets:
    connElems = pyObj.__getattribute__(objSet)

    if not hasattr(connElems, 'all'): continue # Or handle this miss as an err

    objList = list()
    for connElem in connElems.all():
      serializDict = getSerializableElems(connElem)
      if not serializDict: continue

      connConnElems = getForeignKeyElems(connElem, pyObj) 
      refObjs = getConnectedElems(connElem)

      copyDictTo(connConnElems, serializDict)
      copyDictTo(refObjs, serializDict)

      objList.append(serializDict)

    setElemsDict[objSet] = objList
    
  return setElemsDict 

def getTableByKey(tableName, models):
  if not tableName: return None
  tables = getTablesInModels(models)
  return tables.get(tableName, None)

def updateTable(tableObj, updatesBody, updateBool=False):
  # This is to handle the CREATE and UPDATE methods of CRUD
  # Args:
  #  tableObj => ProtoType of the table to be updated
  #  updatesBody => A dict containing the fields to be changed in the table
  #  updateBool  => Set to False, means that you are creating an entry,
  #                 True, means an update 
  #  Note:  If updateBool is set, you MUST provide an 'id' in 'updatesBody'
  if not (tableObj and updatesBody): 
    return dict() # Handle this mishap later

  errorID = -1 
  nChanges = nDuplicates = 0

  if updateBool:
    idToChange = updatesBody.get(globVars.ID_KEY)
    # Only positive IDs
    if not (idToChange and vFuncs.isUnSignedInt(idToChange)):
      print({"error":"Expecting an id to update"})
      return errorID, nChanges, nDuplicates

    objMatch = tableObj.objects.filter((globVars.ID_KEY, idToChange))
    if not objectToChange:
      print({"error":"Could not find the requested ID"})
      return errorID, nChanges, nDuplicates
    objectToChange = objMatch[0]
  else:
    objectToChange = tableObj()

  mutableAttrKeys = filter(
    lambda attr: not (attr.startswith("_") or attr in onlyServerCanWrite), 
    updatesBody
  )
  allowedKeys = getAllowedFilters(objectToChange)
  mutableAttrKeys = list()
  for attr in updatesBody:
    # Don't touch such immutable variables
    if attr.startswith("_") or attr in onlyServerCanWrite:
      continue

    if attr in allowedKeys: # Good to go
      attr = str(attr)

      attrValue = updatesBody.get(attr)
      if updateBool: 
         origValue = objectToChange.__getattribute__(attr)
         if (attrValue == origValue): 
            nDuplicates += 1
            continue

      objectToChange.__setattr__(attr, attrValue)
      nChanges += 1

  if not nChanges: 
    return objectToChange.id, nChanges, nDuplicates

  if updateBool:
    if hasattr(objectToChange, globVars.LAST_TIME_EDIT_KEY):
      objectToChange.__setattr__(globVars.LAST_TIME_EDIT_KEY, getDateInt())
  else:
    if hasattr(objectToChange, globVars.SUBMISSION_DATE_KEY):
      objectToChange.__setattr__(globVars.SUBMISSION_DATE_KEY, getDateInt())
    

  # Let's get that data written to memory
  savedBoolean = saveToMemory(objectToChange)
  if not savedBoolean:
     return errorID, -1, -1
  else:
     return objectToChange.id, nChanges, nDuplicates

def deleteById(objProtoType, targetID):
  # Given a table's name and the targetID, attempt a deletion 
  # Returns: DELETION_FAILURE_CODE on any parameter errors
  #          DELETION_EXCEPTION_CODE on deletion error/exception
  #          DELETION_SUCCESS_CODE on successful deletion
  #   *** The above codes are defined in the globVars file ***

  # Accepting only positive IDs
  if not (objProtoType and vFuncs.isUnSignedInt(targetID)): 
    print("Unknown table ", objProtoType)
    return globVars.DELETION_FAILURE_CODE
  
  targetElem = objProtoType.objects.filter((globVars.ID_KEY, targetID))
  if not targetElem:
    print("Could not find the %s element with id: %s"%(objTypeName, targetID))
    return globVars.DELETION_FAILURE_CODE

  markedElem = targetElem[0] 
  try: 
    markedElem.delete()
  except Exception, e:
    print(e)
    return globVars.DELETION_EXCEPTION_CODE

  else:
    return globVars.DELETION_SUCCESS_CODE

def saveToMemory(newObj):
  if not hasattr(newObj, 'save'): 
     return False

  savBool = False
  try: 
    newObj.save()
  except Exception, e:
    print(e)
    savBool = False # Redundant variable set
  else: 
    savBool = True

  finally:
    return savBool

def getDateInt():
  import datetime as dt
  now = dt.datetime.now()
  ymdHMS = "{y:0>4}{m:0>2}{d:0>2}{H:0>2}{M:0>2}{S:0>2}".format(
    y=now.year, m=now.month, d=now.day, H=now.hour, M=now.minute, S=now.second
  )
  return ymdHMS

def handleHTTPRequest(request, tableName, models):
  requestMethod = request.method

  tableProtoType = getTableByKey(tableName, models)

  if requestMethod == globVars.GET_KEY:
    getBody = request.GET
    return handleGET(getBody, tableProtoType)

  elif requestMethod == globVars.POST_KEY:
    postBody = request.POST
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
  if not tableProtoType: return None

  objDict = tableProtoType.__dict__
  userDefFields = filter(lambda attr:not attr.startswith("_"), objDict)

  return userDefFields

def copyDictTo(src, dest):
  if not (isinstance(src, dict) and isinstance(src, dict)): 
    return

  for srcKey, srcValue in src.items():
    dest[srcKey] = srcValue

######################### CRUD handlers below ########################
def handlePUT(request, tableProtoType):
  response = HttpResponse()

  try:
    body = request.read()
    putBody = json.loads(body)

  except Exception, e:
    print(e)

  else:
    
    data = putBody.get(globVars.DATA_KEY, None)

    results = updateTable(tableProtoType, updateBody=data, updateBool=True)

    changedID, nChanges, nDuplicates = results
    resultsDict =dict(
      id=changedID, nChanges=nChanges, nDuplicates=nDuplicates
    )

    response.write(json.dumps(resultsDict))

  return response

def handleGET(getBody, tableObj):
  response = HttpResponse()
  if not tableObj:
    response.status_code = 403
    response.status_message = "I need a table prototype"
    print("No results")
    return response

  tableObjManager = tableObj.objects
  objCount = tableObjManager.count()

  #========================== FILTRATION HERE ===========================#
  objProto = tableObj()
  bodyAttrs = getAllowedFilters(objProto)
  queriedFilters = getBody.keys()

  allowedFilters = filter(lambda attr:attr in bodyAttrs, queriedFilters)
  dbObjs = tableObjManager
  nFiltrations = 0

  for allowedFilter in allowedFilters:
    filterValue = getBody.get(allowedFilter)
    if not filterValue: continue
    copyObjs = dbObjs
    try:
      copyObjs = copyObjs.filter((allowedFilter, filterValue))
    except:
      continue
    else:
      dbObjs = copyObjs
      nFiltrations += 1

  if not nFiltrations: # Only invalid filters were passed in
     dbObjs = tableObjManager.all()
  #======================================================================#
 
  #===================== Pagination and OffSets here ====================#
  limit = getBody.get(globVars.LIMIT_KEY, None)
  if not limit: 
    limit=0

  # Only postive limits accepted
  elif not vFuncs.isUnSignedInt(limit):
    limit = globVars.THRESHOLD_LIMIT
  else:  
    limit = int(limit)
  
  offSet = getBody.get(globVars.OFFSET_KEY, None)

  # Only accept positive offsets
  if not (offSet and vFuncs.isUnSignedInt(offSet)):
    offSet = globVars.THRESHOLD_OFFSET
  else:
    offSet = int(offSet)
 
  maxSize = dbObjs.count()
  if limit > maxSize: limit = maxSize 
  elif limit: limit += offSet

  #========================== SORTING HERE ==============================#
  sortKey = getBody.get(globVars.SORT_KEY, None)
  sortKey, reverseTrue = translateSortKey(sortKey)
  if sortKey not in bodyAttrs: 
     sortKey = "-%s"%(globVars.ID_KEY)

  elif reverseTrue: 
     sortKey = "-%s"%(sortKey)
  
  dbObjs = dbObjs.order_by(str(sortKey))

  #======================================================================#

  #========================= FORMAT HERE ================================#
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

  for dbObj in dbObjIterator:
    dbElemDict = getSerializableElems(dbObj)
    foreignKeyElems = getForeignKeyElems(dbObj)
    if foreignKeyElems:  copyDictTo(foreignKeyElems, dbElemDict)
    
    if connectedObjsBool: 
      connElems = getConnectedElems(dbObj)
      if connElems: copyDictTo(connElems, dbElemDict)

    data.append(dbElemDict)

  metaDict = dict(
    count=objCount, format=formatKey,sort=sortKey, limit=limit, offset=offSet
  )

  responseDict = dict(meta=metaDict, data=data)

  response.write(json.dumps(responseDict))

  return response

def handlePOST(postBody, tableProtoType):
  response = HttpResponse()

  data = postBody.get(globVars.DATA_KEY, None)
  results = updateTable(
    tableProtoType, updatesBody=postBody, updateBool=False
  )

  resultsDict = dict()

  if results:
    changedID, nChanges, nDuplicates = results
    resultsDict =\
      dict(id=changedID, nChanges=nChanges, nDuplicates=nDuplicates)
  else:
    response.status_code = httpStatusCodes.BAD_REQUEST  

  response.write(json.dumps(resultsDict))

  return response

def handleDELETE(request, tableProtoType):
  response = HttpResponse()
  try:
    body = request.read()
    deleteBody = json.loads(body)
  except Exception, e:
    print(e)
  else:
    targetID = deleteBody.get(globVars.ID_KEY, None)
    resultStatus = deleteById(tableProtoType, targetID)
    resultsDict = dict(resultStatus=resultStatus, id=targetID)

    response.write(json.dumps(resultsDict))

  return response
