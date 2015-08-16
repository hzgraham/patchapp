from django.db import models
import datetime
from django.utils import timezone
import urllib
import parser

class Hosttotal(models.Model):
    env = models.CharField(max_length=128)
    total = models.IntegerField(default=0)
    def __unicode__(self):
        return self.hosttotal

class Errata(models.Model):
    RHEA = models.CharField(max_length=128, null=True, blank=True)
    RHSA = models.CharField(max_length=128, null=True, blank=True)
    RHBA = models.CharField(max_length=128, null=True, blank=True)
    def __unicode__(self):
        #return self.
        return '%s %s %s' % (self.RHEA, self.RHSA, self.RHBA)

class Server(models.Model):
    server = models.CharField(max_length=256, null=True, blank=True)
    exclude = models.TextField(max_length=256, null=True, blank=True)
    skip = models.BooleanField(default=True)
    hostgroup = models.CharField(max_length=50, null=True, blank=True)
    comments = models.TextField(max_length=256, null=True, blank=True)
    satid = models.IntegerField(default=0)
    env = models.CharField(max_length=50, null=True, blank=True)
    updates = models.TextField(max_length=1000, null=True, blank=True)
    def __unicode__(self):
        return self.server
