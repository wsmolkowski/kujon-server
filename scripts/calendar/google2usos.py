#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import datetime
import getpass
import json
import sys

import atom.data
import gdata.calendar.client
import oauth2
import urlparse
from usos2google_conf import *

try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree

parser=argparse.ArgumentParser(description="""Simple program using USOS API and Google Calendar Data API to copy your sked to google. See http://winemore.w.staszic.waw.pl/usos2google.html for more info.""")
parser.add_argument('-s', '--short', action="store_true", default=False, help='Shorten some predefined names')
parser.add_argument('-u', '--user', help='Your google account name')
parser.add_argument('-p', '--password', help="Your google account password (do not use this option if you don't have to, program will ask for your password!)")
args=parser.parse_args()

# Shortening

def ts(id, fallback):
 return id
def ns(id,fallback):
 if names_dict and (id in names_dict):
  return names_dict[id]
 return fallback

def types_short(i):
 return ts(i['classtype_id'], i['classtype_name']['pl'])
def names_short(i):
 return ns(i['course_id'], i['course_name']['pl'])

# USOS authentication

def empty(s):
 if(not s):
  return True
 if(s=='insert_here'):
  return True
 if(s=='insert_here_if_you_want'):
  return True

if (empty(usosapi_base_url) or empty(consumer_key) or empty(consumer_secret)):
 exit("Fill the settings first.")

usosapi_base_url_secure = usosapi_base_url.replace("http://", "https://")
consumer = oauth2.Consumer(consumer_key, consumer_secret)


if not empty(access_token_key):
 access_token = oauth2.Token(access_token_key, access_token_secret)

else:
 request_token_url = usosapi_base_url_secure + 'services/oauth/request_token?scopes=studies|offline_access'
 authorize_url = usosapi_base_url + 'services/oauth/authorize'
 access_token_url = usosapi_base_url_secure + 'services/oauth/access_token'
 # Step 1. Request Token
 usosc = oauth2.Client(consumer)
 resp, content = usosc.request(request_token_url, "GET", callback_url='oob')
 if resp['status'] != '200':
  raise Exception("Invalid response %s:\n%s" % (resp['status'], content))
 def _read_token(content):
  arr = dict(urlparse.parse_qsl(content))
  return oauth2.Token(arr['oauth_token'], arr['oauth_token_secret'])
 request_token = _read_token(content)
 # Step 2. Obtain authorization
 print "Go to the following link in your browser:"
 print "%s?oauth_token=%s" % (authorize_url, request_token.key)
 print
 oauth_verifier = raw_input('What is the PIN code? ')
 # Step 3. Access Token
 request_token.set_verifier(oauth_verifier)
 usosc = oauth2.Client(consumer, request_token)
 resp, content = usosc.request(access_token_url, "GET")
 try:
  access_token = _read_token(content)
 except KeyError:
  print "Cound not retrieve Access Token (invalid PIN?)."
  sys.exit(1)
 print
 print "*** You may want to hardcode these values, so you won't need to reauthorize ***"
 print "access_token_key = '%s'" % access_token.key
 print "access_token_secret = '%s'" % access_token.secret

usosc = oauth2.Client(consumer, access_token)

# Google authorization

if(not args.user):
 args.user=raw_input("Enter your google account username: ")
if(not args.password):
 args.password=getpass.getpass("Enter your google account password: ")
googlec=gdata.calendar.client.CalendarClient(source="usos2google-v1")
try:
 googlec.ClientLogin(args.user, args.password, googlec.source)
except gdata.client.BadAuthentication:
  exit('Bad username or password')
except gdata.client.Error:
  exit('Login Error')

# Google calendar query and (selection or creation)

feed = googlec.GetOwnCalendarsFeed()
print "Select calendar to copy sked to:"
cals=[]
alink=None
for i, cal in enumerate(feed.entry):
 print ' %s. %s' % (i, cal.title.text)
 cals+=[cal]
i=int(i)+1
print " %d. Create new calendar" % i
num=raw_input("Enter number [%d]: " % i)
if(num==""):
 num=i
else:
 num=int(num)
if(num==i):
 name=raw_input("Enter name for the new calendar: ")
 calendar = gdata.calendar.data.CalendarEntry()
 calendar.title = atom.data.Title(text=name)
 calendar.summary = atom.data.Summary(text='Sked imported from USOS by usos2google')
 calendar.timezone = gdata.calendar.data.TimeZoneProperty(value=mytz.zone)
 calendar.hidden = gdata.calendar.data.HiddenProperty(value='false')
 try:
  calendar=googlec.InsertCalendar(new_calendar=calendar)
 except gdata.client.RequestError as e:
  print "Error while creating calendar:"
  print e
  sys.exit(1)
 alink=calendar.GetAlternateLink()
else:
 alink=cals[num].GetAlternateLink()

# Event retrieval and creation, week by week, starting with last monday.

total=int(raw_input("Number of weeks to copy (starting from last monday): "))

day=datetime.date.today()
while day.isoweekday()>1:
 day=day-datetime.timedelta(days=1)
sday=day

def u2gt(s):
 """Converts time string retreived from USOS to one acceptable by google"""
 t=mytz.localize(datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S"))
 return (t-t.utcoffset()).strftime('%Y-%m-%dT%H:%M:%S.000Z')

print "Copying events, this may take a while."

for i in xrange(total):
 sys.stdout.write("%d. week: " % (i+1))
 resp, content = usosc.request(usosapi_base_url + "services/tt/student?start=%s&days=7&fields=name|start_time|end_time|classtype_name|classtype_id|course_name|course_id|building_id|building_name|room_number|classgroup_profile_url" % day.isoformat()  ,"GET")
 if resp['status'] != '200':
  raise Exception("USOS Invalid response %s.\n%s" % (resp['status'], content))
 items = json.loads(content)
 for i in items:
  event = gdata.calendar.data.CalendarEventEntry()
  if(args.short):
   event.title = atom.data.Title(text="%s: %s     %s" % (types_short(i), names_short(i), i['room_number']))
  else:
   event.title = atom.data.Title(text=i['name']['pl'])
  event.content = atom.data.Content(i['classgroup_profile_url'])
  event.where.append(gdata.calendar.data.CalendarWhere(value=("%s %s" % (i['room_number'],i['building_name']['pl']))))
  event.when.append(gdata.calendar.data.When(start=u2gt(i['start_time']), end=u2gt(i['end_time'])))
  googlec.InsertEvent(event, alink.href)
  sys.stdout.write('.')
  sys.stdout.flush()
 day+=datetime.timedelta(days=7)
 sys.stdout.write('\n')

