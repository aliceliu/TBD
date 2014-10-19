#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
import logging
import urllib
import urllib2

import json

from google.appengine.api import urlfetch

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template = jinja_environment.get_template("home.html")
        self.response.out.write(template.render(template_values))

class GiveHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        url = 'https://api.locu.com/v2/venue/search'
        form_fields = {
          "api_key" : "f165c0e560d0700288c2f70cf6b26e0c2de0348f",
          "fields" : [ "name", "location", "contact", "categories" ],
          "venue_queries" : [
            {
              "location" : {
                "geo" : {
                  "$in_lat_lng_radius" : [40.693134, -119.882813, 99999]
                }
              }
            }
          ]
        }

        form_data = json.dumps(form_fields)
        json_result = urlfetch.fetch(url=url,
            payload=form_data,
            method=urlfetch.POST,
            headers={'Content-Type': 'application/x-www-form-urlencoded'})

        result = json.loads(json_result.content)
        venue_names = []
        for venue in result['venues']:
          venue_names.append(venue['name'].encode('ascii','ignore'))

        template_values['venue_names'] = venue_names
        template = jinja_environment.get_template("give.html")
        self.response.out.write(template.render(template_values))

class FindHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template = jinja_environment.get_template("find.html")
        self.response.out.write(template.render(template_values))

class AutocompleteHandler(webapp2.RequestHandler):
    def post(self):
        url = 'https://api.locu.com/v2/venue/search'
        form_fields = {
          "api_key" : "f165c0e560d0700288c2f70cf6b26e0c2de0348f",
          "fields" : [ "name", "location", "contact", "categories" ],
          "venue_queries" : [
            {
              "location" : {
                "geo" : {
                  "$in_lat_lng_radius" : [40.693134, -119.882813, 99999]
                }
              }
            }
          ]
        }

        form_data = json.dumps(form_fields)
        json_result = urlfetch.fetch(url=url,
            payload=form_data,
            method=urlfetch.POST,
            headers={'Content-Type': 'application/x-www-form-urlencoded'})

        result = json.loads(json_result.content)
        venue_names = []
        for venue in result['venues']:
          venue_names.append(venue['name'].encode('ascii','ignore'))

        response = {
          'd': venue_names,
        }
        self.response.out.write(json.dumps(response))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/give', GiveHandler),
    ('/find', FindHandler),
    ('/autocomplete', AutocompleteHandler),
], debug=True)
