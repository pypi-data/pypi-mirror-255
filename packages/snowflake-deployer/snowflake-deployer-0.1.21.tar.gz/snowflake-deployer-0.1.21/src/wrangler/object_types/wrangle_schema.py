from src.util.util import remove_prefix
import threading
from time import sleep

def _get_grants(self_sf, full_schema_name:str, grant_dict:dict):
    grants_raw = self_sf._sf.grants_get(full_schema_name, 'schema')
    grant_dict[full_schema_name] = grants_raw

def _get_tag_references(self_sf, database_name:str, full_schema_name:str, tag_dict:dict):
    tags_raw = self_sf._sf.tag_references_get(database_name, full_schema_name, 'schema')
    tag_dict[full_schema_name] = tags_raw

def wrangle_schema(self, database_name:str, env_database_prefix:str, env_role_prefix:str, deploy_db_name:str, ignore_roles_list:str, deploy_tag_list:list[str], current_role:str, available_roles:list[str], handle_ownership, semaphore)->dict:
    if env_database_prefix is None:
        env_database_prefix = ''
    if env_role_prefix is None:
        env_role_prefix = ''

    schemas = self._sf.schemas_get(database_name)  
    
    # Get tags & grants async for performce
    threads_all = []
    tag_dict = {}
    grant_dict = {}
    for s in schemas:
        full_schema_name = database_name + '.' + s['SCHEMA_NAME']

        # async get all role grants
        _get_grants(self, full_schema_name, grant_dict)
        #thread_name = 'schemagrants_'+full_schema_name
        #t = threading.Thread(target=_get_grants, name=thread_name, args=(self, semaphore, full_schema_name, grant_dict))
        #threads_all.append(t)

        # async get all tag grants
        _get_tag_references(self, database_name, full_schema_name, tag_dict)
        #thread_name = 'schematags_'+full_schema_name
        #t = threading.Thread(target=_get_tag_references, name=thread_name, args=(self, semaphore, database_name, full_schema_name, tag_dict))
        #threads_all.append(t)

    # async management
    for t in threads_all:
        t.start()
    #for t in threads_all:
    #    t.join()
    while ( len(list(filter(lambda t: t.name.startswith('schemagrants_'), threading.enumerate()))) > 0
           or len(list(filter(lambda t: t.name.startswith('schematags_'), threading.enumerate()))) > 0 ):
        sleep(1)

    #while len(threading.enumerate()) > 1:
    #    print(threading.enumerate())
    #    #sleep(1)

    data = []
    for s in schemas:
        full_schema_name = database_name + '.' + s['SCHEMA_NAME']
        if s['SCHEMA_NAME'] not in ['INFORMATION_SCHEMA']:    
            
            s['OWNER_SANS_JINJA'] = s['OWNER']
            s['OWNER'] = self._handle_ownership(handle_ownership, s['OWNER'], 'schema', full_schema_name, current_role, available_roles)

            if s['OWNER'] not in ignore_roles_list: # if role managed by deployer (not out of the box) then add the jinja reference
                s['OWNER'] = self.create_jinja_role_instance(s['OWNER'])
            s['DATABASE_NAME'] = database_name
            s['FULL_SCHEMA_NAME'] = full_schema_name
            
            schema_with_db = database_name + '.' + s['SCHEMA_NAME']
            tags = []
            tags_sans_jinja = []
            #tags_raw = self._sf.tag_references_get(database_name, schema_with_db, 'schema') #warehouse tag references live within Snowflake db
            tags_raw = tag_dict[full_schema_name]
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
            s['TAGS'] = tags
            s['TAGS_SANS_JINJA'] = tags_sans_jinja
            
            #grants_raw = self._sf.grants_get(schema_with_db, 'schema')
            grants_raw = grant_dict[full_schema_name]
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
            s['GRANTS_SANS_JINJA'] = grants_combined_sans_jinja
            s['GRANTS'] = grants_combined

            data.append(s)
    
    return data   
