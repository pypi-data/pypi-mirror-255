from src.util.util import remove_prefix
import threading
from time import sleep

def _get_grants(self_sf, full_func_name:str, grant_dict:dict):
    grants_raw = self_sf._sf.grants_get(full_func_name, 'function')
    grant_dict[full_func_name] = grants_raw

def _get_tag_references(self_sf, database_name:str, full_func_name:str, tag_dict:dict):
    tags_raw = self_sf._sf.tag_references_get(database_name, full_func_name, 'function') 
    tag_dict[full_func_name] = tags_raw
        
def wrangle_function(self, database_name:str, env_function_prefix:str, env_database_prefix:str, env_role_prefix:str, deploy_db_name:str, ignore_roles_list:str, deploy_tag_list:list[str], current_role:str, available_roles:list[str], handle_ownership, semaphore)->dict:
    if env_function_prefix is None:
        env_function_prefix = ''
    if env_database_prefix is None:
        env_database_prefix = ''
    if env_role_prefix is None:
        env_role_prefix = ''

    funcs = self._sf.functions_get(database_name)  
    
    # Get tags & grants async for performce
    threads_all = []
    grant_dict = {}
    tag_dict = {}
    for f in funcs:
        schema_name = f['SCHEMA_NAME']
        full_func_name = database_name + '.' + schema_name + '.' + f['ARGUMENT_SIGNATURE_TO_MATCH'].replace(' ','')

        # async get all role grants
        _get_grants(self, full_func_name, grant_dict)
        #thread_name = 'functiongrants_'+full_func_name
        #t = threading.Thread(target=_get_grants, name=thread_name, args=(self, semaphore, full_func_name, grant_dict))
        #threads_all.append(t)

        # async get all tag grants
        _get_tag_references(self, database_name, full_func_name, tag_dict)
        #thread_name = 'functiontags_'+full_func_name
        #t = threading.Thread(target=_get_tag_references, name=thread_name, args=(self, semaphore, database_name, full_func_name, tag_dict))
        #threads_all.append(t)

    # async management
    #for t in threads_all:
    #    t.start()
    #for t in threads_all:
    #    t.join()

    

    data = []
    for f in funcs:
        schema_name = f['SCHEMA_NAME']
        full_function_name = database_name + '.' + schema_name + '.' + f['FUNCTION_NAME'].replace(' ','')
        f['FUNCTION_NAME_SANS_ENV'] = remove_prefix(f['FUNCTION_NAME'],env_function_prefix)
        
        f['OWNER_SANS_JINJA'] = f['OWNER']
        f['OWNER'] = self._handle_ownership(handle_ownership, f['OWNER'], 'function', full_function_name, current_role, available_roles)
        
        if f['OWNER'] not in ignore_roles_list: # if role managed by deployer (not out of the box) then add the jinja reference
            f['OWNER'] = self.create_jinja_role_instance(f['OWNER'])
        
        
        full_func_name = database_name + '.' + schema_name + '.' + f['ARGUMENT_SIGNATURE_TO_MATCH'].replace(' ','')
        f['FULL_FUNCTION_NAME'] = full_func_name
        tags = []
        tags_sans_jinja = []
        #tags_raw = self._sf.tag_references_get(database_name, full_func_name, 'function') #warehouse tag references live within Snowflake db
        
        #print('$$$$$$$$$$$$$$$$$$$')
        #print(full_func_name)
        #print(tag_dict)
        #print('$$$$$$$$$$$$$$$$$$$')

        tags_raw = tag_dict[full_func_name]
        for t in tags_raw:
            if not (t['TAG_DATABASE'] == deploy_db_name and t['TAG_SCHEMA'] == 'TAG' and t['TAG_NAME'] in deploy_tag_list):
                tv = {}
                db_name = remove_prefix(t['TAG_DATABASE'],env_database_prefix)
                #tv['name'] = self.create_jinja_ref(db_name, t['TAG_SCHEMA'], t['TAG_NAME'])
                #tv['value'] = t['TAG_VALUE']
                tag_name = self.create_jinja_ref(db_name, t['TAG_SCHEMA'], t['TAG_NAME'])
                tv[tag_name] = t['TAG_VALUE']
                tags.append(tv)

                tv_sans_jinja = {}
                tag_name_sans_jinja = t['TAG_DATABASE'] + '.' + t['TAG_SCHEMA'] + '.' + t['TAG_NAME']
                tv_sans_jinja[tag_name_sans_jinja] = t['TAG_VALUE']
                tags_sans_jinja.append(tv_sans_jinja)
        f['TAGS'] = tags
        f['TAGS_SANS_JINJA'] = tags_sans_jinja

        #grants_raw = self._sf.grants_get(full_func_name, 'function')
        grants_raw = grant_dict[full_func_name]
        grants = []
        grants_sans_jinja = []
        for g in grants_raw:
            if g['PRIVILEGE'] != 'OWNERSHIP' and g['GRANTEE_NAME'] != current_role and g['GRANT_TYPE'] == 'ROLE':
                grant = {}
                role_name = remove_prefix(g['GRANTEE_NAME'],env_role_prefix)
                grant_to = self.create_jinja_role_instance(role_name) if role_name not in ignore_roles_list else role_name
                grant[grant_to] = g['PRIVILEGE']
                if g['GRANT_OPTION'] is True:
                    grant['GRANT_OPTION'] = True
                grants.append(grant)

                grant_sans_jinja = {}
                grant_sans_jinja[g['GRANTEE_NAME']] = g['PRIVILEGE']
                if g['GRANT_OPTION'] is True:
                    grant_sans_jinja['GRANT_OPTION'] = True
                grants_sans_jinja.append(grant_sans_jinja)
        grants_combined = self._combine_grants(grants)
        grants_combined_sans_jinja = self._combine_grants(grants_sans_jinja)
        f['GRANTS_SANS_JINJA'] = grants_combined_sans_jinja
        f['GRANTS'] = grants_combined

        f.pop('ARGUMENT_SIGNATURE_TO_MATCH')
        data.append(f)
    
    return data   
