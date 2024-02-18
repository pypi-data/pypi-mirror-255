import src.common.common as cmn
import json
def hash_object(self, data_retention_time_in_days:int, comment:str, owner:str, change_tracking:bool, tags:list, columns:list, grants:list, row_access_policy:dict)->str:
    data_retention_time_in_days_n = data_retention_time_in_days if data_retention_time_in_days is not None else ''
    comment_n = comment if comment is not None else ''
    owner_n = owner if owner is not None else ''
    change_tracking_n = change_tracking if change_tracking is not None else ''

    tags_n = tags if tags is not None else []
    columns_n = columns if columns is not None else []
    grants_n = grants if grants is not None else []
    row_access_policy_n = row_access_policy if row_access_policy is not None else {}

    #print('$$$')
    #print('---1---')
    #print(columns_n)
    

    new_cols = []
    for c in columns_n:
        nc = {}
        nc['NAME'] = c['NAME']
        nc['TAGS'] = c['TAGS'] if 'TAGS' in c and c['TAGS'] != '' and c['TAGS'] is not None else []
        nc['TAGS'] = cmn.sort_list_of_dicts_by_key(nc['TAGS'])
        #if c['TAGS'] is not None:
        #    print('is not none')
        #else:
        #    print('it is none')
        new_cols.append(nc)
    columns_n = new_cols

    #print('---2---')
    #print(columns_n)
    
    columns_n = cmn.sort_list_of_dicts(columns_n)
    #print('---3---')
    #print(columns_n)
    tags_n = cmn.sort_list_of_dicts(tags_n)
    grants_n = cmn.sort_list_of_dicts(grants_n)
    row_access_policy_n = dict(sorted(row_access_policy_n.items(), key=lambda item: item[1]))

    tpl = (data_retention_time_in_days_n, comment_n, owner_n, change_tracking_n, tags_n, columns_n, grants_n, row_access_policy_n)
    
    json_string = json.dumps(tpl)
    #print('---4---')
    #print(json_string)
    #print('$$$end')

    hash_value = self.hash(tpl)
    return hash_value

