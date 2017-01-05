#!/usr/bin/env python

import webapp2
import json

class ApiHandler(webapp2.RequestHandler):
    def get(self):
        api_dict = {'questions': []}
        self.response.write(json.dumps(api_dict, sort_keys=True))

app = webapp2.WSGIApplication([
    ('/', ApiHandler),
    ('/api', ApiHandler),
], debug=True)

