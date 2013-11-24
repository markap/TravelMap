"""
Using redirect route instead of simple routes since it supports strict_slash
Simple route: http://webapp-improved.appspot.com/guide/routing.html#simple-routes
RedirectRoute: http://webapp-improved.appspot.com/api/webapp2_extras/routes.html#webapp2_extras.routes.RedirectRoute
"""

from webapp2_extras.routes import RedirectRoute
from web import handlers
secure_scheme = 'https'

_routes = [
    RedirectRoute('/story/', handlers.StoryHandler, name='story', strict_slash=True),
    RedirectRoute('/story.register/', handlers.StoryRegisterHandler, name='storyregister', strict_slash=True),
    RedirectRoute('/story.edit/<storyid>', handlers.StoryEditHandler, name='storyedit', strict_slash=True),
    RedirectRoute('/story.delete/<storyid>', handlers.StoryDeleteHandler, name='storydelete', strict_slash=True),
    RedirectRoute('/story.detail/<storyid>', handlers.StoryDetailHandler, name='storydetail', strict_slash=True),
    RedirectRoute('/story.addlocation/<storyid>', handlers.StoryAddLocationHandler, name='storyaddlocation', strict_slash=True),
    RedirectRoute('/story.editlocation/<storyid>/<locationindex>', handlers.StoryEditLocationHandler, name='storyeditlocation', strict_slash=True),
    RedirectRoute('/story.deletelocation/<storyid>/<locationindex>', handlers.StoryDeleteLocationHandler, name='storydeletelocation', strict_slash=True),
    RedirectRoute('/trip/<storyid>', handlers.TripHandler, name='trip', strict_slash=True),
    RedirectRoute('/explore/', handlers.ExploreHandler, name='explore', strict_slash=True),
    RedirectRoute('/search/', handlers.SearchHandler, name='search', strict_slash=True),
    RedirectRoute('/google.search/', handlers.GoogleSearchHandler, name='googlesearch', strict_slash=True),
    RedirectRoute('/wikipedia.search/', handlers.WikipediaHandler, name='wikisearch', strict_slash=True),
    RedirectRoute('/story.search/', handlers.StorySearchHandler, name='storysearch', strict_slash=True),
    RedirectRoute('/story.image.upload/<storyid>/<locationkey>', handlers.StoryImageUploadHandler, name='storyimage', strict_slash=True),
    RedirectRoute('/story.image.delete/<storyid>/<locationkey>/<blobkey>', handlers.StoryImageDeleteHandler, name='storyimagedelete', strict_slash=True),
    RedirectRoute('/serve/<blobkey>', handlers.ServeHandler, name='serve', strict_slash=True),
    
]

def get_routes():
    return _routes

def add_routes(app):
    if app.debug:
        secure_scheme = 'http'
    for r in _routes:
        app.router.add(r)