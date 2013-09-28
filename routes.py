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
    RedirectRoute('/trip/', handlers.TripHandler, name='trip', strict_slash=True),
    RedirectRoute('/explore/', handlers.ExploreHandler, name='explore', strict_slash=True),
    RedirectRoute('/search/', handlers.SearchHandler, name='search', strict_slash=True),
]

def get_routes():
    return _routes

def add_routes(app):
    if app.debug:
        secure_scheme = 'http'
    for r in _routes:
        app.router.add(r)