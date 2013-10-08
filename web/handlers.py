# -*- coding: utf-8 -*-

"""
    A real simple app for using webapp2 with auth and session.

    It just covers the basics. Creating a user, login, logout
    and a decorator for protecting certain handlers.

    Routes are setup in routes.py and added in main.py
"""
import httpagentparser
from google.appengine.ext import ndb

from boilerplate import models
from boilerplate.lib.basehandler import BaseHandler, JSONHandler
from boilerplate.lib.decorators import user_required

from datetime import datetime

from web import models as m, parser



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
        story.dateto = datetime.strptime(dateto, '%d/%m/%Y'),
        story.datefrom = datetime.strptime(datefrom, '%d/%m/%Y'),
        story.desc = self.request.get('desc')
               
        self.print_json()        
                


class StoryDetail(JSONHandler):
    
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
    def post(self, storyid, locationindex):
        story = m.Story.get_by_id(int(storyid))
        
        target_location = None
                
        for loc in story.locations:
            if loc.locationindex == locationindex:
                loc['name'] = self.request.get('name')
                loc['desc'] = self.request.get('desc')
                target_location = loc
                break
        

        story.put()    
        
        self.msg.add_record('location', target_location)
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
