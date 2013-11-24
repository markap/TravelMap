from google.appengine.ext import ndb
from google.appengine.api import search

_STORY_INDEX = 'STORY'


def tokenize(phrase):
    a = []
    for word in phrase.split():
        j = 1
        while True:
            for i in range(len(word) - j + 1):
                a.append(word[i:i + j])
            if j == len(word):
                break
            j += 1
    return ','.join(a)




class Story(ndb.Model):
    name = ndb.StringProperty(required=True)
    dateto = ndb.DateProperty()
    datefrom = ndb.DateProperty()
    desc = ndb.StringProperty()
    
    location_index = ndb.IntegerProperty(default=0)
    locations = ndb.JsonProperty(default=[])
    
    latitude = ndb.FloatProperty()
    longitude = ndb.FloatProperty()
    
    
    
    def _get_story_document(self):
        """Creates a search.Document from an user."""
        
        
        fields = [search.TextField(name='name', value=tokenize(self.name)),
                  search.TextField(name='desc', value=tokenize(self.desc))]
                                   
        for location in self.locations:
            idx = location['locationindex']
            fields.append(search.TextField(name='loc_name_' + str(idx), value=tokenize(location['name'])))
            fields.append(search.TextField(name='loc_desc_' + str(idx), value=tokenize(location['desc'])))
            if 'wikipedia' in location:
                fields.append(search.TextField(name='loc_wiki_' + str(idx), value=tokenize(location['wikipedia'])))
            
        return search.Document(doc_id=str(self.key.id()), fields=fields)
    
    
    def delete_from_index(self):
        search.Index(name=_STORY_INDEX).delete(str(self.key.id())) 

    def put_to_index(self):
        search.Index(name=_STORY_INDEX).put(self._get_story_document())
        
        
    @staticmethod
    def search_index(query_string):
    
        query_string = " OR ".join(query_string.split())
    
    
        result = []
        try:
        
            query = search.Query(query_string=query_string)#, options=options)

            index = search.Index(name=_STORY_INDEX)
            return index.search(query)    
        except search.Error:
            pass
            # log
        return result
    