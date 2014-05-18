# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Constants for thebear

# Table string names
SONG_TABLE_KEY = "Song"
ARTIST_TABLE_KEY = "Artist"

import math
import sys
pyVersion = sys.hexversion/(1<<24)
MAX_INT = sys.maxint if pyVersion < 3 else sys.maxsize

# Max values
MAX_DIGITS = math.floor(math.log(MAX_INT, 2))
assert(MAX_DIGITS >= 1) # Sanity check

MAX_TIME_DIGITS = MAX_DIGITS
MAX_HASH_LENGTH = 400 #Arbitrary value here
MAX_DECIMAL_PLACES = 5 # Arbitrarily
MAX_MISC_STR_LENGTH = 200
MAX_COMMENT_LENGTH = 1000 #Arbitrary value here

