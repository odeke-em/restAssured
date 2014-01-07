#!/usr/bin/python

# Global variables defined here
# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Copyright (c) 2014

MAX_HASH_LENGTH = 400 #Arbitrary value here
MAX_COMMENT_LENGTH = 1000 #Arbitrary value here

#Http Request Methods
GET_KEY = "GET"
PUT_KEY = "PUT"
POST_KEY = "POST"
DELETE_KEY = "DELETE"

#Element attribute keys
ID_KEY = "id"
STATUS_KEY = "status"
LAST_TIME_EDIT_KEY = "lastTimeEdit"
SUBMISSION_DATE_KEY = "submissionDate"

DATA_KEY = "data"
TARGET_TABLE_KEY = "targetTable"

NUMERICAL_DIV_ATTR = "__div__" # Number-like objects accept division
FORMAT_NUMBER_ATTR = "format_number" # For handling DecimalFields

SORT_KEY = "sort"
FORMAT_KEY = "format"
REVERSE_KEY = "_r"

#Format types
LONG_FMT_KEY = "long"
SHORT_FMT_KEY = "short"

ID_SUFFIX = "_id"
SET_SUFFIX_RE = "set$"

MAX_DIGITS = 1<<15 # Arbitrary value
MAX_DECIMAL_PLACES = 5 # Arbitrarily
MAX_MISC_STR_LENGTH = 200
DELETION_FAILURE_CODE = -1
DELETION_EXCEPTION_CODE = 0
DELETION_SUCCESS_CODE = 1

SONG_TABLE_KEY = "Song"
PLAYTIME_TABLE_KEY = "PlayTime"
SONGENTRY_TABLE_KEY = "SongEntry"
