# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Constants for Uploader
import math

# Table string names
BLOB_TABLE_KEY = "Blob"
BLOB_CHECKSUM_TABLE_KEY = "BlobCheckSum"

MAX_COMMENT_LENGTH  = 1000 #Arbitrary value here
MAX_MISC_STR_LENGTH = 400
MAX_BLOB_LENGTH_BYTES = 1024 * 1024 * 50 # 50MB max length => Arbitrarily
MAX_ENCODING_STR_LENGTH = 200 # Arbitrary value

import sys
pyVersion = sys.hexversion/(1<<24)
MAX_INT = sys.maxint if pyVersion < 3 else sys.maxsize

import math
# Max values
MAX_DIGITS = math.floor(math.log(MAX_INT, 2))
assert(MAX_DIGITS >= 1) # Sanity check

MAX_BLOB_DIGITS = math.ceil(math.log10(MAX_BLOB_LENGTH_BYTES))
assert(MAX_BLOB_DIGITS >= 1)

MAX_CHECKSUM_LENGTH = 64 # Arbitrary
MAX_ALGONAME_LENGTH = 40 # Arbitrary
