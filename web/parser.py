

def ndb_list_parser(query_obj):
    return [ndb_obj_parser(entry) for entry in query_obj]

def ndb_obj_parser(query_obj):
    d = query_obj.to_dict()
    d['id'] = query_obj.key.id()
    return d