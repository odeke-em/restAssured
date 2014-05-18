# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Constants for GCS
# Table string names
IMAGE_TABLE_KEY = "Image"
LABEL_TABLE_KEY = "Label"
MARKER_TABLE_KEY = "Marker"

import sys
pyVersion = sys.hexversion/(1<<24)
MAX_INT = sys.maxint if pyVersion < 3 else sys.maxsize

import math
# Max values
MAX_DIGITS = math.floor(math.log(MAX_INT, 2))
assert(MAX_DIGITS >= 1) # Sanity check

MAX_TIME_DIGITS = MAX_DIGITS
MAX_DECIMAL_PLACES = 8 # Arbitrarily
MAX_COMMENT_LENGTH  = 1000 #Arbitrary value here
MAX_MISC_STR_LENGTH = 400
MAX_BLOB_LENGTH_BYTES = (1024 * 1024 * 50) # 50MB max length => Arbitrarily
