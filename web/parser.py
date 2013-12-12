
"""
    Parses a list of query objects to be printed as json
"""
def ndb_list_parser(query_obj, remove_location=False):
    return [ndb_obj_parser(entry, remove_location) for entry in query_obj]


"""
    Parses a query object to be printed as json
"""
def ndb_obj_parser(query_obj, remove_location=False):
    d = query_obj.to_dict()
    if remove_location == True:
        del d['datefrom']
        del d['dateto']
        del d['locations']
    d['id'] = query_obj.key.id()
    return d