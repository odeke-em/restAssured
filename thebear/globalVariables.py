#!/usr/bin/python

# Global variables defined here
# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Copyright (c) 2014
#Http Request Methods
GET_KEY = "GET"
PUT_KEY = "PUT"
POST_KEY = "POST"
DELETE_KEY = "DELETE"

#Element attribute keys
ID_KEY = "id"
STATUS_KEY = "status"
LAST_EDIT_TIME_KEY = "lastEditTime"
SUBMISSION_DATE_KEY = "submissionDate"

DATA_KEY = "data"
TARGET_TABLE_KEY = "targetTable"

NUMERICAL_DIV_ATTR = "__div__" # Number-like objects accept division
FORMAT_NUMBER_ATTR = "format_number" # For handling DecimalFields

SORT_KEY = "sort"
LIMIT_KEY = "limit"
FORMAT_KEY = "format"
REVERSE_KEY = "_r"

# Format keys
LONG_FMT_KEY = "long"
SHORT_FMT_KEY = "short"
OFFSET_KEY = "offset"

ID_SUFFIX = "_id"
SET_SUFFIX_RE = "set$"

# Max values
MAX_DIGITS = 1<<15 # Arbitrary value
MAX_HASH_LENGTH = 400 #Arbitrary value here
MAX_DECIMAL_PLACES = 5 # Arbitrarily
MAX_MISC_STR_LENGTH = 200
MAX_COMMENT_LENGTH = 1000 #Arbitrary value here

# Failure codes
DELETION_FAILURE_CODE = -1
DELETION_EXCEPTION_CODE = 0
DELETION_SUCCESS_CODE = 1

# Thresholds here
THRESHOLD_LIMIT = 50
THRESHOLD_OFFSET = 0

# Table string names
SONG_TABLE_KEY = "Song"
PLAYTIME_TABLE_KEY = "PlayTime"
SONGENTRY_TABLE_KEY = "SongEntry"
