# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Constants for GCS

# Table string names
IMAGE_TABLE_KEY = "Image"
LABEL_TABLE_KEY = "Label"
MARKER_TABLE_KEY = "Marker"

# Function to determine bit length of unsigned ints
# Enable some tail recursion
bitLength = lambda i,l=1 : l if i <= 1 else bitLength(i>>1, l+1)

import sys
pyVersion = sys.hexversion/(1<<24)
MAX_INT = sys.maxint if pyVersion < 3 else sys.maxsize

# Max values
MAX_DIGITS = bitLength(MAX_INT)
assert(MAX_DIGITS >= 1) # Sanity check

MAX_TIME_DIGITS = MAX_DIGITS
MAX_DECIMAL_PLACES = 8 # Arbitrarily
MAX_COMMENT_LENGTH  = 1000 #Arbitrary value here
MAX_MISC_STR_LENGTH = 400
MAX_BLOB_LENGTH_BYTES = (1024 * 1024 * 50) # 50MB max length => Arbitrarily
