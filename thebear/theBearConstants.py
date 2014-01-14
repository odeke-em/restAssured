# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Constants for thebear

# Table string names
SONG_TABLE_KEY = "Song"
PLAYTIME_TABLE_KEY = "PlayTime"
SONGENTRY_TABLE_KEY = "SongEntry"

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
MAX_HASH_LENGTH = 400 #Arbitrary value here
MAX_DECIMAL_PLACES = 5 # Arbitrarily
MAX_MISC_STR_LENGTH = 200
MAX_COMMENT_LENGTH = 1000 #Arbitrary value here

