#!/usr/bin/env python

import webapp2
import json
import jinja2
import os
import yaml

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

class TopicHandler(webapp2.RequestHandler):
    '''
    Allows us to add topics
    '''
    def get(self):
        template_values = {}

        with open('categories.yaml', 'r') as f:
            category_dict = yaml.load(f)

        template_values['categories'] = category_dict
        template = JINJA_ENVIRONMENT.get_template('admin.html')
        self.response.write(template.render(template_values))

class ApiHandler(webapp2.RequestHandler):
    '''
    Handles API requests
    '''
    def get(self):
        category_list = self.request.get('categories', '')
        categories = category_list.split(',')

        with open('categories.yaml', 'r') as f:
            category_dict = yaml.load(f)

        topics = []
        for cat in categories:
            if cat not in category_dict:
                self.error(400)
            topics.extend(category_dict[cat])

        api_dict = {'topics': topics}
        self.response.write(json.dumps(api_dict, sort_keys=True))

app = webapp2.WSGIApplication([
    ('/', TopicHandler),
    ('/admin', TopicHandler),
    ('/api', ApiHandler),
], debug=True)

