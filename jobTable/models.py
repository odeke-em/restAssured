from django.db import models

import constants

class Worker(models.Model):
    name = models.CharField(default='JobBot', max_length=constants.MAX_NAME_LENGTH)
    purpose = models.CharField(max_length=constants.MAX_PURPOSE_LENGTH)

    def __unicode__(self):
        return 'Name: %s Purpose: %s'%(self.name, self.purpose)
class Job(models.Model):
    status = models.CharField(
        default=constants.FRESH_STATUS,
        max_length=constants.MAX_STATUS_LENGTH, choices=constants.STATUS_CHOICES
    )
    
    author  = models.CharField(max_length=constants.MAX_AUTHOR_LENGTH)
    message = models.CharField(max_length=constants.MAX_MESSAGE_LENGTH)
    response = models.CharField(max_length=constants.MAX_RESPONSE_LENGTH)
    metaData = models.CharField(max_length=constants.MAX_METADATA_LENGTH)

    dateCreated = models.DateTimeField(auto_now_add=True) # Automatically set on first object creation
    lastEditTime = models.DateTimeField(auto_now=True) # Automatically set after every save

    assignedWorker = models.ForeignKey(Worker)
    def __unicode__(self):
        return 'Status: %s. Message: %s Author: %s'%(
            self.status, self.message, self.author
        )

class Route(models.Model):
    address = models.CharField(max_length=constants.MAX_ADDRESS_LENGTH) 
    location = models.CharField(max_length=constants.MAX_LOCATION_LENGTH)
    lastEditTime = models.DateTimeField(auto_now=True)
    dateCreated = models.DateTimeField(auto_now_add=True)
    metaData = models.CharField(max_length=constants.MAX_METADATA_LENGTH)

    def __unicode__(self):
        return 'Route:%s'%(self.address)
