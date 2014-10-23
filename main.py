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

import sys
sys.path.insert(0, 'libs')

import oauth2

API_HOST = 'api.yelp.com'
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'San Francisco, CA'
SEARCH_LIMIT = 3
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'

LOCATION = 'Berkeley'

# OAuth credential placeholders that must be filled in by users.
CONSUMER_KEY = 'VEaqAkY_fwQexWrMqSe-jw'
CONSUMER_SECRET = '--C-Uu9Et6IK1S8RXrFxCEYFgZ4'
TOKEN = '7H2qxt0nWDOHQdWAHK6AuFQVt_ZVHrbI'
TOKEN_SECRET = 'wly6FbbcYD9IbnUp-LzBk9RJNtU'

from google.appengine.api import urlfetch

from models import *

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

MY_RECOMMENDATIONS = ["McDonald's", "Nicole Won", "Kevin Casey", "Gavin Chu"]
CURRENT_USER = "Alice Liu"

def make_yelp_request(host, path, url_params=None):
    """Prepares OAuth authentication and sends the request to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.

    Returns:
        dict: The JSON response from the request.

    Raises:
        urllib2.HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    encoded_params = urllib.urlencode(url_params)

    url = 'http://{0}{1}?{2}'.format(host, path, encoded_params)

    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    oauth_request = oauth2.Request('GET', url, {})
    oauth_request.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': TOKEN,
            'oauth_consumer_key': CONSUMER_KEY
        }
    )
    token = oauth2.Token(TOKEN, TOKEN_SECRET)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = oauth_request.to_url()

    print 'Querying {0} ...'.format(url)

    conn = urllib2.urlopen(signed_url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()

    return response

class LandingPageHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template = jinja_environment.get_template("landing.html")
        self.response.out.write(template.render(template_values))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template = jinja_environment.get_template("home.html")
        self.response.out.write(template.render(template_values))

class GiveHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}

        friends = []
        for friend in Friendship.gql("WHERE from_user_name = :1", CURRENT_USER):
          friends.append(friend.to_user_name.encode('ascii','ignore'))

        template_values['friends'] = friends
        template = jinja_environment.get_template("give.html")
        self.response.out.write(template.render(template_values))
    def post(self):
        print self.request.get('business')
        print self.request.get_all('friends')
        print self.request.get('comment')

        business_id = self.request.get('business_id')
        business_path = BUSINESS_PATH + business_id

        yelp_result = make_yelp_request(API_HOST, business_path)

        yelp_url = 'http://www.yelp.com/biz/' + business_id

        Recommendation(from_user_name=CURRENT_USER, to_user_name=CURRENT_USER, business_name=self.request.get('business'), status="unread", category=self.request.get('categories_string'), comment=self.request.get('comment'), yelp_url=yelp_url, image_url=yelp_result['image_url']).put()

        self.redirect('/mobile')

class FindHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        if self.request.get('status'):
          template_values['recommendations'] = Recommendation.gql("WHERE to_user_name = :1 AND status = :2", CURRENT_USER, self.request.get('status'))
        else:
          template_values['recommendations'] = Recommendation.gql("WHERE to_user_name = :1", CURRENT_USER)
        template = jinja_environment.get_template("find.html")
        self.response.out.write(template.render(template_values))

class DetailHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template_values['recommendation'] = Recommendation.get(self.request.get('id'))
        template = jinja_environment.get_template("detail.html")
        self.response.out.write(template.render(template_values))

class AutocompleteYelpHandler(webapp2.RequestHandler):
    def post(self):
        url_params = {
            'term': eval(self.request.body)['q'],
            'location': LOCATION,
            'is_closed': False,
            'limit': 10
        }

        yelp_results = make_yelp_request(API_HOST, SEARCH_PATH, url_params=url_params)

        venue_names = []
        for venue in yelp_results['businesses']:
          venue_names.append({
            'name': venue['name'].encode('ascii','ignore'),
            'id': venue['id'].encode('ascii','ignore')
          })

        return self.response.out.write(json.dumps(venue_names))

class AutocompleteYelpPictureHandler(webapp2.RequestHandler):
    def post(self):
        business_id = eval(self.request.body)['id']
        business_path = BUSINESS_PATH + business_id

        yelp_result = make_yelp_request(API_HOST, business_path)

        return self.response.out.write(json.dumps(yelp_result))

class ResetAndSeedHandler(webapp2.RequestHandler):
    def get(self):
        query = Recommendation.all(keys_only=True)
        entries = query.fetch(1000)
        db.delete(entries)

        query = User.all(keys_only=True)
        entries = query.fetch(1000)
        db.delete(entries)

        query = Friendship.all(keys_only=True)
        entries = query.fetch(1000)
        db.delete(entries)

        User(name='Kevin Casey').put()
        User(name='Alice Liu').put()
        User(name='Nicole Won').put()
        User(name='Gavin Chu').put()

        Friendship(from_user_name='Alice Liu', to_user_name='Kevin Casey').put()
        Friendship(from_user_name='Alice Liu', to_user_name='Nicole Won').put()
        Friendship(from_user_name='Alice Liu', to_user_name='Gavin Chu').put()

        Recommendation(from_user_name='Kevin Casey', to_user_name='Alice Liu', business_name="Lucky House Thai", status="unread", yelp_url="http://www.yelp.com/biz/lucky-house-thai-berkeley", category="Thai", image_url='http://s3-media1.fl.yelpcdn.com/bphoto/w-9FrR3QLeeclQk8k2u2ug/l.jpg', comment="this place seems legit").put()
        Recommendation(from_user_name='Gavin Chu', to_user_name='Alice Liu', business_name="Gather", status="read", yelp_url='http://www.yelp.com/biz/gather-berkeley', category="American (New), Breakfast & Brunch", image_url="http://www.opentable.com/img/restimages/36430.jpg", comment="This food was great, you should go here with Kevin").put()

        self.response.out.write('success')

app = webapp2.WSGIApplication([
    ('/', LandingPageHandler),
    ('/mobile', MainHandler),
    ('/give', GiveHandler),
    ('/find', FindHandler),
    ('/detail', DetailHandler),
    ('/autocomplete_yelp', AutocompleteYelpHandler),
    ('/autocomplete_yelp_picture', AutocompleteYelpPictureHandler),
    ('/reset', ResetAndSeedHandler),
], debug=True)
