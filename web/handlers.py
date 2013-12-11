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
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore

import urllib
from datetime import datetime
import json
import wiki2plain, wikipedia

from web import models as m, parser, wiki2plain
from web import blobstore as blob




class ExploreHandler(BaseHandler):
    
    def get(self, **kwargs):
        """
        user_info = models.User.get_by_id(long(self.user_id))
        params = {
            "user_info": user_info
        }
        """
        
        params = {
            "stories": parser.ndb_list_parser(m.Story.query(), True)
        }
        
        print params
        
        return self.render_template('explore.html', **params)


class SearchHandler(BaseHandler):
    
    def get(self, **kwargs):
               
        
        return self.render_template('search.html')

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
        story.put_to_index()
        
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
        story.put_to_index()
               
        self.print_json()        
    
    
class StoryDeleteHandler(JSONHandler):
    
    def post(self, storyid):  
        story = m.Story.get_by_id(int(storyid))
        story.key.delete()
        story.delete_from_index()
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
            'longitude': float(self.request.get('longitude')),
            'wikipedia': self.request.get('wikipedia')
        }
        print '#########'
        print location
        
        story.locations.append(location)
        story.put()
        story.put_to_index()
        
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
        story.put_to_index()
        
        self.msg.add_record('location', target_location)
        self.print_json()
        
    
     

class GoogleSearchHandler(JSONHandler):
    def post(self):
        text = self.request.get('text')
        print "############"
        print text
        #text = 'jeju'
        
        url = "https://www.googleapis.com/customsearch/v1?key=AIzaSyBVGHr3UpamcOQkLPP7guMalOZ0l2VZO6k&cx=006720223612486791407:aet3a3qxagc&q=%s" % urllib.quote_plus(text)
        result = urlfetch.fetch(url)
        print result.content
        if result.status_code == 200:
            links = []
            j = json.loads(result.content)
            #self.response.out.write(j)
            #print j['items']
            #self.response.out.write(type(j))
            for content in j['items']:
                
                if ".jpg" not in content['link'].lower() or ".png" not in content['link'].lower():
                    links.append({'title': content['title'], 
                                  'link': content['link'].split('/')[-1]})
                 
            self.msg.add_record('content', links)
            
        self.print_json()
        


        
    
        
class WikipediaHandler(JSONHandler):
    def post(self):
        
        url = self.request.get('url')
        
        
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
        story.put_to_index()
        self.print_json()
        
        
class StorySearchHandler(JSONHandler):
    def post(self):
        
        text = self.request.get('text')
        result = m.Story.search_index(text)

        stories = [parser.ndb_obj_parser(m.Story.get_by_id(int(r.doc_id)), True) for r in result]


        self.msg.add_record("result", stories)
        self.print_json()
        
    def get(self):
        self.post()

            
        
class TripHandler(BaseHandler):
    
    #@user_required
    def get(self, storyid, **kwargs):
        """user_info = models.User.get_by_id(long(self.user_id))
        params = {
            "user_info": user_info
        }
        """
        

        params = {
            "story": parser.ndb_obj_parser(m.Story.get_by_id(int(storyid)))
        }
        
        return self.render_template('trip.html', **params)
    
    
class StoryImageUploadHandler(JSONHandler): 

    def post(self, storyid, locationid):
        # @todo make it secure
        data = self.request.POST['file']
        print "######################################"
        print data
        
        story = m.Story.get_by_id(int(storyid))
                
        if data.type.find('image') != -1:
            key = blob.write_blob(data)
            
            for k, location in enumerate(story.locations):
                if int(location['locationindex']) == int(locationid):
                    story.locations[k].setdefault('images', []).append(key)
                    break
        
            story.put()
        
            self.msg.add_record('locations', story.locations)
        
        else:
            self.msg.add_error('Fileupload not allowed')
        
        self.print_json()
        

class StoryImageDeleteHandler(JSONHandler):
    
    def post(self, storyid, locationid, blobkey):   
        blob_key = str(urllib.unquote(blobkey))
        story = m.Story.get_by_id(int(storyid))
        
        for k, location in enumerate(story.locations):
            if int(location['locationindex']) == int(locationid):
                if blob_key in location['images']:
                    story.locations[k]['images'].remove(blob_key)
                    break
        
        story.put()
        
        self.msg.add_record('locations', story.locations)       
        self.print_json()
        
            
        
class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler, JSONHandler):
    
    def get(self, blobkey):
        blob_key = str(urllib.unquote(blobkey))
        if not blobstore.get(blob_key):
            self.error(404)
            return
        
        self.send_blob(blobstore.BlobInfo.get(blob_key), save_as=False)
        
        
        
        
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
