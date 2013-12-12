import json


"""
    Message object for handling and printing json data
    Allows to handle data records and errors
"""
class Message:


    error = []

    record = {}


    def add_error(self, error):
        self.error.append(error)
        
 
    def add_record(self, key, value):
        self.record[key] = value

    def has_error(self):
        return len(self.error) != 0

    def clear(self):
        self.error = []
        self.record = {}

    def __str__(self):

        status = 'OK' if self.has_error() == False else 'ERROR'
        return json.dumps({'status': status,
                     'error': self.error,
                     'record': self.record}).replace("&amp;", "&");

