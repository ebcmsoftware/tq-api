#!/usr/bin/env python

import webapp2
import json
import jinja2
import os
import yaml
import time

from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

class Category(ndb.Model):
    '''
    topic_data will be stored as a dict of dicts containing Gtrends data. For example,
    topic_data = {
        'obama': {
            'December 2003': 0.0,
            'November 2008': 100.0,
            'December 2008': 98.0,
            ...
        },
        'trump': {
            'December 2003': 9.0,
            'November 2008': 69.0,
            'December 2008': 42.0,
            ...
        },
        ...
    }
    '''
    name = ndb.StringProperty()
    topics = ndb.StringProperty(repeated=True)
    topic_data = ndb.JsonProperty()

class TopicHandler(webapp2.RequestHandler):
    '''
    Allows us to add topics
    '''
    def get(self):
        template_values = {}

        cats = Category.query().fetch()

        template_values['categories'] = cats
        template = JINJA_ENVIRONMENT.get_template('admin.html')
        self.response.write(template.render(template_values))

    def post(self):
        '''
        When u wanna add a new topic, this is the endpoint u wanna call
        '''
        cat = self.request.get('category')
        topic = self.request.get('topic')
        if not cat:
            self.error(400)
        elif cat and not topic:
            key = ndb.Key('Category', cat.lower())
            new_category = Category(parent=key, name=cat.lower(), topics=[])
            new_category.put()
        else:
            key = ndb.Key('Category', cat.lower())
            cat = Category.query(ancestor=key).fetch()[0]
            cat.topics.append(topic)
            cat.put()
        time.sleep(.25)
        self.redirect('/admin')


class DeleteHandler(webapp2.RequestHandler):
    '''
    Resopnsible for deleting categories or topics
    '''
    def post(self):
        cat = self.request.get('category')
        topic = self.request.get('topic')
        if not cat:
            self.error(400)
        elif cat and not topic:
            category = Category.query(Category.name == cat).fetch()[0]
            category.key.delete()
        else:
            category = Category.query(Category.name == cat).fetch()[0]
            category.topics = [x for x in category.topics if x != topic]
            category.put()
        time.sleep(.25)
        self.redirect('/admin')


class TrendDataHandler(webapp2.RequestHandler):
    '''
    Handles adding stuff (via jason) to the categories.

    Required params: 
    * category (i.e., 'politics')
    * topic (i.e., 'trump')
    * topic_data (as a dict of trends data, in the format specified above: i.e., {'December 2016': 98.0, ...})
    '''
    def post(self):
        cat = self.request.get('category')
        topic = self.request.get('topic')
        data = self.request.get('topic_data')
        if not (cat and topic and topic_data):
            self.error(400)
        topic_dict = json.loads(data)
        category = Category.query(Category.name == cat).fetch()[0]
        if not category.topic_dict:
            category.topic_dict = {}
        # TODO: play around with some play data, get it showing. make sure it's in there and appendable. 
        category.topic_dict[topic] = topic_dict
        category.put()


class ApiHandler(webapp2.RequestHandler):
    '''
    Handles API requests
    '''
    def get(self):
        category_list = self.request.get('categories', '')
        categories = category_list.split(',')

        categories = Category.query(Category.name.IN(categories))

        topics = []
        for cat in categories:
            topics.extend(cat.topics)

        api_dict = {'topics': topics}
        self.response.write(json.dumps(api_dict, sort_keys=True))

app = webapp2.WSGIApplication([
    ('/', TopicHandler),
    ('/delete', DeleteHandler),
    ('/add_trends_data', TrendDataHandler),
    ('/admin', TopicHandler),
    ('/api', ApiHandler),
], debug=True)

