# -*- coding: utf-8 -*-

"""
    A real simple app for using webapp2 with auth and session.

    It just covers the basics. Creating a user, login, logout
    and a decorator for protecting certain handlers.

    Routes are setup in routes.py and added in main.py
"""
import httpagentparser
from google.appengine.ext import ndb
from google.appengine.api import urlfetch

from boilerplate import models
from boilerplate.lib.basehandler import BaseHandler, JSONHandler
from boilerplate.lib.decorators import user_required

from datetime import datetime
import json
import wiki2plain, wikipedia

from web import models as m, parser, wiki2plain



class ExploreHandler(BaseHandler):
    
    def get(self, **kwargs):
        """
        user_info = models.User.get_by_id(long(self.user_id))
        params = {
            "user_info": user_info
        }
        """
        return self.render_template('explore.html')#, **params)


class SearchHandler(BaseHandler):
    
    def get(self, **kwargs):
        params = {
            "stories": [{"name" : "Busan"}, {"name" : "Daejeon"}, {"name" : "Jeju"}, {"name" : "Tokyo"}]
        }
        
        
        return self.render_template('search.html', **params)

class StoryHandler(BaseHandler):
    
    #@user_required
    def get(self, **kwargs):
        """
        user_info = models.User.get_by_id(long(self.user_id))
        params = {
            "user_info": user_info
        }
        """
     
        params = {
            "stories": parser.ndb_list_parser(m.Story.query())
        }
        
        print params
        return self.render_template('story.html', **params)
       
    
class StoryRegisterHandler(JSONHandler):
    
    #@user_required
    def post(self):
        
        dateto = self.request.get('dateto')
        datefrom = self.request.get('datefrom')
        
        story = m.Story(name=self.request.get('name'),
                     dateto=datetime.strptime(dateto, '%d/%m/%Y'),
                     datefrom=datetime.strptime(datefrom, '%d/%m/%Y'),
                     desc=self.request.get('desc'))
        
        storykey = story.put()
        
        self.msg.add_record('storykey', storykey.id())
        self.print_json()
        

class StoryEditHandler(JSONHandler):
    
    def post(self, storyid):
        story = m.Story.get_by_id(int(storyid))
        dateto = self.request.get('dateto')
        datefrom = self.request.get('datefrom')
        
        story.name = self.request.get('name')
        story.dateto = datetime.strptime(dateto, '%d/%m/%Y')
        story.datefrom = datetime.strptime(datefrom, '%d/%m/%Y')
        story.desc = self.request.get('desc')
        story.put()
               
        self.print_json()        
    
    
class StoryDeleteHandler(JSONHandler):
    
    def post(self, storyid):  
        story = m.Story.get_by_id(int(storyid))
        story.key.delete()
        self.print_json()          


class StoryDetailHandler(JSONHandler):
    
    def post(self, storyid):
        story = m.Story.get_by_id(int(storyid))
        self.msg.add_record('locations', story.locations)
        self.print_json()
    
class StoryAddLocationHandler(JSONHandler):
    
    #@user_required
    def post(self, storyid):
        story = m.Story.get_by_id(int(storyid))
        
        location_index = story.location_index
        story.location_index += 1
        
        story.latitude = float(self.request.get('latitude'))
        story.longitude = float(self.request.get('longitude'))
        
        location = {
            'locationindex': location_index,
            'name': self.request.get('name'),
            'desc': self.request.get('desc'),
            'latitude': float(self.request.get('latitude')),
            'longitude': float(self.request.get('longitude'))
        }
        
        story.locations.append(location)
        story.put()
        
        self.msg.add_record('location', location)
        self.print_json()
    
    
class StoryEditLocationHandler(JSONHandler):
    
    #@user_required
    def get(self, storyid, locationindex):
        story = m.Story.get_by_id(int(storyid))
        
        target_location = None
                
        for k, loc in enumerate(story.locations):
            if loc['locationindex'] == int(locationindex):
                self.msg.add_record(k, locationindex)
                story.locations[k]['name'] = self.request.get('name')
                story.locations[k]['desc'] = self.request.get('desc')
                target_location = loc
                break
        

        story.put()    
        
        self.msg.add_record('location', target_location)
        self.print_json()
        
    
     

class GoogleSearchHandler(JSONHandler):
    def post(self):
        text = self.request.get('location')
        text = "busan"
        
        url = "https://www.googleapis.com/customsearch/v1?key=AIzaSyBVGHr3UpamcOQkLPP7guMalOZ0l2VZO6k&cx=006720223612486791407:aet3a3qxagc&q=%s" % text
        result = urlfetch.fetch(url)
        if result.status_code == 200:
            links = []
            j = json.loads(result.content)
            print j['items']
            self.response.out.write(type(j))
            for content in j['items']:
                
                if ".jpg" not in content['link'].lower() or ".png" not in content['link'].lower():
                    links.append({'title': content['title'], 
                                  'link': content['link'].split('/')[-1]})
                 
            self.msg.add_record('content', links)
            
        self.print_json()
        
    def get(self):
        self.post()
        
        
class WikipediaHandler(JSONHandler):
    def post(self):
        
        url = self.request.get('url')
        url = "Busan"
        
        
        wiki = wikipedia.Wikipedia('en')

        try:
            raw = wiki.article(url)
        except:
            raw = None
        
        if raw:
            wiki2plain_ = wiki2plain.Wiki2Plain(raw)
            content = wiki2plain_.unwiki(wiki2plain_.text).split("==")[0]
            self.msg.add_record("wiki", content)
            
        self.print_json()
    
    
    
    def get(self):
        self.post()


class StoryDeleteLocationHandler(JSONHandler):
    def post(self, storyid, locationindex):
        
        story = m.Story.get_by_id(int(storyid))
        
        # delete location
        for k, loc in enumerate(story.locations):
            if loc['locationindex'] == int(locationindex):
                del story.locations[k]
                break
            
        # update main coordinates
        for loc in story.locations:
            story.latitude = loc['latitude']
            story.longitude = loc['longitude']

        story.put()
        self.print_json()
class TripHandler(BaseHandler):
    
    #@user_required
    def get(self, storyid, **kwargs):
        """user_info = models.User.get_by_id(long(self.user_id))
        params = {
            "user_info": user_info
        }
        """
        
        print ndb.Key('Story', int(storyid)).get()
        print m.Story.get_by_id(int(storyid))
        params = {
            "story": parser.ndb_obj_parser(m.Story.get_by_id(int(storyid)))
        }
        
        return self.render_template('trip.html', **params)
    

class SecureRequestHandler(BaseHandler):
    """
    Only accessible to users that are logged in
    """

    @user_required
    def get(self, **kwargs):
        user_session = self.user
        user_session_object = self.auth.store.get_session(self.request)

        user_info = models.User.get_by_id(long(self.user_id))
        user_info_object = self.auth.store.user_model.get_by_auth_token(
            user_session['user_id'], user_session['token'])

        try:
            params = {
                "user_session": user_session,
                "user_session_object": user_session_object,
                "user_info": user_info,
                "user_info_object": user_info_object,
                "userinfo_logout-url": self.auth_config['logout_url'],
            }
            return self.render_template('secure_zone.html', **params)
        except (AttributeError, KeyError), e:
            return "Secure zone error:" + " %s." % e
