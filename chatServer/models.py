# Author: Konrad Lindenbach <klindenb@ualberta.ca>,
#         Emmanuel Odeke <odeke@ualberta.ca>

# Copyright (c) 2014

from django.db import models

# Local module
import chatServerConstants

class Receipient(models.Model):
    name = models.CharField(max_length=chatServerConstants.MAX_NAME_LENGTH)
    alias = models.CharField(max_length=chatServerConstants.MAX_ALIAS_LENGTH, blank=True)

    dateCreated = models.DateTimeField(auto_now_add=True) # Automatically set on first object creation
    lastEditTime = models.DateTimeField(auto_now=True) # Automatically set after every save
    token = models.CharField(max_length=chatServerConstants.MAX_TOKEN_LENGTH)
    photoUri = models.CharField(max_length=chatServerConstants.MAX_PROFILE_URI_LENGTH, blank=True)

    def __unicode__(self):
        return "Receipient:<%s aka %s>"%(self.name, self.alias)

class Message(models.Model):
    sender = models.ForeignKey(Receipient, related_name='message_sender')
    receipient = models.ForeignKey(Receipient, related_name='message_receipient')

    # If parentMessage is not null, this is a reply
    parentMessage = models.ForeignKey('Message', blank=True, null=True)

    body = models.CharField(max_length=chatServerConstants.MAX_BODY_LENGTH, blank=True)
    subject = models.CharField(max_length=chatServerConstants.MAX_SUBJECT_LENGTH, blank=True)

    dateCreated = models.DateTimeField(auto_now_add=True) # Automatically set on first object creation
    lastEditTime = models.DateTimeField(auto_now=True) # Automatically set after every save

    def __unicode__(self):
        return "Message<%s>"%(self.subject)

class MessageMarker(models.Model):
    receipient = models.ForeignKey(Receipient)
    associatedMessage = models.ForeignKey(Message)

    dateCreated = models.DateTimeField(auto_now_add=True) # Automatically set on first object creation
    lastEditTime = models.DateTimeField(auto_now=True) # Automatically set after every save

    def __unicode__(self):
        return "MessageMarker:: %s=>%s"%(self.receipient, self.associatedMessage)
