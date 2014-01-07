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

import models
import httpStatusCodes
import validatorFunctions as vFs
import globalVariables as globVars

# Set to False during deployment
DEVELOPER_MODE = True

# Dict to detect elements that by default are non json-serializable 
# but whose converters make them json-serializable
trivialSerialzdDict = {
  lambda e: e is None: lambda e:"null",
  lambda s: hasattr(s, globVars.NUMERICAL_DIV_ATTR): str
}

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

def getTablesInModels():
  # Returns a dict mapping table names to their objects,
  # for every table defined in models.py
  tableNameToTypeDict = dict()
  for classTuple in inspect.getmembers(models, inspect.isclass):
    name, obj = classTuple 
    tableNameToTypeDict[name] = obj

  return tableNameToTypeDict

def getTableObjByKey(tableKeyName):
  # Returns the table object given the tableKeyName(a string)
  # if it is exists in the DB, else None
  if not tableKeyName: return None
  tablesInDB = getTablesInModels()
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
    if inspect.isfunction(quantifier):
      if quantifier(value):
         # Let's get the converted value and test for serializability
         serialized = converter(value)
         if isSerializable(serialized): return serialized

def suffixStrip(key, suffix):
  if not (key and suffix): return None

  beforeSuffixSearch = re.search("(.*)%s"%(suffix), key)
  if not beforeSuffixSearch: return None

  return beforeSuffixSearch.groups(1)[0]

def matchTable(tableKey):
  allTables = getTablesInModels()
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

def getTableByKey(tableName):
  if not tableName: return None
  tables = getTablesInModels()
  return tables.get(tableName, None)

def updateTable(tableName, updatesBody, updateBool=False):
  # This is to handle the CREATE and UPDATE methods of CRUD
  # Args:
  #  tableName => a string of the table to be updated
  #  updatesBody => A dict containing the fields to be changed in the table
  #  updateBool  => Set to False, means that you are creating an entry,
  #                 True, means an update 
  #  Note:  If updateBool is set, you MUST provide an 'id' in 'updatesBody'
  tableObj = getTableByKey(tableName)
  if not (tableObj and updatesBody): 
    return dict() # Handle this mishap later

  errorID = -1 
  nChanges = nDuplicates = 0

  if updateBool:
    idToChange = updatesBody.get(globVars.ID_KEY)
    if not (idToChange and vFs.isInt(idToChange)):
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

def deleteById(objTypeName, targetID):
  # Given a table's name and the targetID, attempt a deletion 
  # Returns: DELETION_FAILURE_CODE on any parameter errors
  #          DELETION_EXCEPTION_CODE on deletion error/exception
  #          DELETION_SUCCESS_CODE on successful deletion
  #   *** The above codes are defined in the globVars file ***
  if not (objTypeName and vFs.isInt(targetID)): 
    return globVars.DELETION_FAILURE_CODE

  objProtoType = getTableByKey(objTypeName)
  if not objProtoType: 
    print("Could not find the table %s"%(objTypeName))
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

def handleHTTPRequest(request, tableName):
  requestMethod = request.method

  if requestMethod == globVars.GET_KEY:
    getBody = request.GET
    return handleGET(getBody, tableName)

  elif requestMethod == globVars.POST_KEY:
    postBody = request.POST
    return handlePOST(postBody, tableName)

  elif requestMethod == globVars.DELETE_KEY:
    return handleDELETE(request, tableName)

  elif requestMethod == globVars.PUT_KEY:
    return handlePUT(request, tableName)
  
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
def handlePUT(request, tableName):
  response = HttpResponse()

  try:
    body = request.read()
    putBody = json.loads(body)

  except Exception, e:
    print(e)

  else:
    if not tableName:
      print("A tableName is needed")
      response.status_code = httpStatusCodes.BAD_REQUEST  
    
    data = putBody.get(globVars.DATA_KEY, None)

    results = updateTable(tableName, updateBody=data, updateBool=True)

    changedID, nChanges, nDuplicates = results
    resultsDict =dict(
      id=changedID, nChanges=nChanges, nDuplicates=nDuplicates
    )

    response.write(json.dumps(resultsDict))

  return response

def handleGET(getBody, tableName):
  response = HttpResponse()
  tableObj = getTableByKey(tableName)
  if not tableObj:
    if DEVELOPER_MODE: tableObj = getTableByKey("Song")
    else:
      response.status_code = 403
      response.status_message = "Cannot find the table %s"%(tableName)
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
  #======================================================================#

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

  for dbObj in dbObjs:
    dbElemDict = getSerializableElems(dbObj)
    foreignKeyElems = getForeignKeyElems(dbObj)
    if foreignKeyElems:  copyDictTo(foreignKeyElems, dbElemDict)
    
    if connectedObjsBool: 
      connElems = getConnectedElems(dbObj)
      if connElems: copyDictTo(connElems, dbElemDict)

    data.append(dbElemDict)

  metaDict = dict(count=objCount, format=formatKey,sort=sortKey)
  responseDict = dict(meta=metaDict, data=data)

  response.write(json.dumps(responseDict))

  return response

def handlePOST(postBody, tableName):
  response = HttpResponse()

  data = postBody.get(globVars.DATA_KEY, None)
  targetID = postBody.get(globVars.ID_KEY, None)
  results = updateTable(tableName, updatesBody=postBody, updateBool=False)
  resultsDict = dict()

  if results:
    changedID, nChanges, nDuplicates = results
    resultsDict =\
      dict(id=changedID, nChanges=nChanges, nDuplicates=nDuplicates)

  response.write(json.dumps(resultsDict))

  return response

def handleDELETE(request, tableName):
  response = HttpResponse()
  try:
    body = request.read()
    deleteBody = json.loads(body)
  except Exception, e:
    print(e)
  else:
    if not tableName:
      print("A tableName is needed")
      response.status_code = httpStatusCodes.BAD_REQUEST  

    targetID = deleteBody.get(globVars.ID_KEY, None)
    resultStatus = deleteById(tableName, targetID)
    resultsDict = dict(resultStatus=resultStatus)

    response.write(json.dumps(resultsDict))

  return response
