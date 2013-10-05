from google.appengine.ext import ndb



class Story(ndb.Model):
    name = ndb.StringProperty(required=True)
    dateto = ndb.DateProperty()
    datefrom = ndb.DateProperty()
    desc = ndb.StringProperty()
    
    location_index = ndb.IntegerProperty(default=0)
    locations = ndb.JsonProperty(default=[])
    
    latitude = ndb.FloatProperty()
    longitude = ndb.FloatProperty()
    