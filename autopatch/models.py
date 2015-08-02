from django.db import models
import datetime
from django.utils import timezone
import urllib
#from sgmllib import SGMLParser
import parser

class HostList():
    def get_urls_from(self, url):
        url_list = []
        usock = urllib.urlopen(url)
        parser = URLLister()
        parser.feed(usock.read())
        usock.close()
        parser.close()
        map(url_list.append,
            [item for item in parser.urls \
             if item.startswith(('http', 'ftp', 'www'))])
        return url_list

# class URLLister(SGMLParser):
#     def reset(self):
#         SGMLParser.reset(self)
#         self.urls = []

#     def start_a(self, attrs):
#         href = [v for k, v in attrs if k=='href']
#         if href:
#             self.urls.extend(href)
class Hosttotal(models.Model):
    env = models.CharField(max_length=128)
    total = models.IntegerField(default=0)
    def __unicode__(self):
        return self.hosttotal

class Server(models.Model):
    server = models.CharField(max_length=256, null=True, blank=True)
    exclude = models.TextField(max_length=256, null=True, blank=True)
    skip = models.CharField(max_length=25, null=True, blank=True)
    hostgroup = models.CharField(max_length=50, null=True, blank=True)
    def __unicode__(self):
        return self.server

    #active_status = models.BooleanField(default=0)
    #def is_active(self):
    #    return bool(active_status)

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    def was_published_recently(self):
        now = timezone.now()
        # return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

    
class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    def __unicode__(self):
        return self.name

class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)
    def __unicode__(self):
        return self.title
