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
    # exclude - packages that are to be excluded, can include globs
    exclude = models.TextField(max_length=256, null=True, blank=True)
    # skip - whether the host will be skipped or not
    skip = models.BooleanField(default=True)
    hostgroup = models.CharField(max_length=50, null=True, blank=True)
    owner = models.CharField(max_length=50, null=True, blank=True)
    comments = models.TextField(max_length=256, null=True, blank=True)
    satid = models.IntegerField(default=0)
    env = models.CharField(max_length=50, null=True, blank=True)
    # updates - all available errata
    updates = models.TextField(max_length=2000, null=True, blank=True)
    # Planned errata that hasn't been updated
    plerrata = models.TextField(max_length=2000, null=True, blank=True)
    # uptodate - true if server is updated
    uptodate = models.BooleanField(default=0)
    def __str__(self):
        return '%s' % (self.server)

# Model containing syspatch_owner entries
# that will be ignored by views and templates
class Owner(models.Model):
    owner = models.CharField(max_length=128)

# For recording when changes occur to other models
class Audit(models.Model):
    server = models.CharField(max_length=256, null=True, blank=True)
    skip = models.BooleanField(default=True)
    exclude = models.TextField(max_length=256, null=True, blank=True)
    hostgroup = models.CharField(max_length=50, null=True, blank=True)
    comments = models.TextField(max_length=256, null=True, blank=True)
    user = models.CharField(max_length=128)
    mod_date = models.DateTimeField(auto_now=True, null=True)

# Model that contains a list of packages affected by each errata
class Packages(models.Model):
    # errata is the name of the errata
    errata = models.CharField(max_length=128, null=True, blank=True)
    # python list of packages that affect the corresponding errata
    pkgs = models.TextField(max_length=2000, null=True, blank=True)
