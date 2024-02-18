import json

def get_sf_database_name(name:str, prefix:str):
    if prefix is None:
        rtn = name 
    else:
        rtn = prefix + name
    return rtn

def get_sf_role_name(name:str, prefix:str):
    if prefix is None:
        rtn = name 
    else:
        rtn = prefix + name
    return rtn

def get_sf_warehouse_name(name:str, prefix:str):
    if prefix is None:
        rtn = name 
    else:
        rtn = prefix + name
    return rtn 

def hash_yml_data(yml_data):
    return hash(json.dumps(yml_data))

#def sort_list_of_dicts(input_list:list[dict])->list[dict]:
#    return sorted(input_list, key=lambda d: list(d.keys())[0])

def sort_list_of_dicts(input_list:list[dict])->list[dict]:
    return sorted(input_list, key=lambda d: d[list(d.keys())[0]])

def sort_list_of_dicts_by_key(input_list:list[dict])->list[dict]:
    return sorted(input_list, key=lambda d: list(d.keys())[0])
