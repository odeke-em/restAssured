# Author: Emmanuel Odeke <odeke@ualberta.ca>

INPROGRESS_STATUS = 'inprogress'
FAILED_STATUS = 'failed'
FINISHED_STATUS = 'finished'
FRESH_STATUS = 'fresh'

JOB_TABLE_KEY = 'Job'
WORKER_TABLE_KEY = 'Worker'

STATUS_CHOICES = (
    (INPROGRESS_STATUS[:2], INPROGRESS_STATUS),
    (FAILED_STATUS[:2], FAILED_STATUS),
    (FINISHED_STATUS[:2], FINISHED_STATUS),
    (FRESH_STATUS[:2], FRESH_STATUS)
)

MAX_STATUS_LENGTH = len(max(STATUS_CHOICES, key=lambda a: a[1])[1])

MAX_NAME_LENGTH = 100 # Arbitrary value
MAX_AUTHOR_LENGTH = 400 # Arbitrary value
MAX_MESSAGE_LENGTH = 1000 # Arbitrary value but taking account things like URLS
MAX_RESPONSE_LENGTH = 500 # Arbitrary value
MAX_PURPOSE_LENGTH = 100 # Arbitrary value
MAX_METADATA_LENGTH = 300 # Arbitrary value
