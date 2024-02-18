from src.util.util import remove_prefix
import threading
from time import sleep

def _get_grants(self_sf, semaphore, database_name:str, grant_dict:dict):
    with semaphore:
        grants_raw = self_sf._sf.grants_get(database_name, 'database')
        grant_dict[database_name] = grants_raw
    
def _get_tag_references(self_sf, semaphore, database_name:str, tag_dict:dict):
    with semaphore:
        tags_raw = self_sf._sf.tag_references_get(database_name, database_name, 'database')
        tag_dict[database_name] = tags_raw
       
def wrangle_database(self, env_database_prefix:str, env_role_prefix:str, excluded_databases:list[str], deploy_db_name:str, ignore_roles_list:str, deploy_tag_list:list[str], current_role:str, available_roles:list[str], handle_ownership, import_databases:list[str], semaphore)->dict:
    if env_database_prefix is None:
        env_database_prefix = ''
    if env_role_prefix is None:
        env_role_prefix = ''
        
    dbs = self._sf.databases_get(env_database_prefix)  
    
    # Get tags & grants async for performce
    threads_all = []
    grant_dict = {}
    tag_dict = {}
    for db in dbs:
        db_name = db['DATABASE_NAME']

        # async get all role grants
        thread_name = 'dbgrants_'+db_name
        t = threading.Thread(target=_get_grants, name=thread_name, args=(self, semaphore, db_name, grant_dict))
        threads_all.append(t)
        #print(thread_name)
        # async get all tag grants
        thread_name = 'dbtags_'+db_name
        t = threading.Thread(target=_get_tag_references, name=thread_name, args=(self, semaphore, db_name, tag_dict))
        threads_all.append(t)
        #print(thread_name)

    # async management
    for t in threads_all:
        t.start()
    for t in threads_all:
        t.join()

    #while ( len(list(filter(lambda t: t.name.startswith('dbgrants_'), threading.enumerate()))) > 0
    #       or len(list(filter(lambda t: t.name.startswith('dbtags_'), threading.enumerate()))) > 0 ):
    #    sleep(1)
    
    #print(grant_dict)
    #print(tag_dict)
    #while len(threading.enumerate()) > 1:
    #    sleep(1)

    data = []
    for db in dbs:
        if db['DATABASE_NAME'] not in excluded_databases and db['DATABASE_NAME'] != deploy_db_name:
            if import_databases == [] or db['DATABASE_NAME'] in import_databases:
                db['DATABASE_NAME_SANS_ENV'] = remove_prefix(db['DATABASE_NAME'],env_database_prefix)   
                
                db['OWNER_SANS_JINJA'] = db['OWNER']
                db['OWNER'] = self._handle_ownership(handle_ownership, db['OWNER'], 'database', db['DATABASE_NAME'], current_role, available_roles)
                
                if db['OWNER'] not in ignore_roles_list: # if role managed by deployer (not out of the box) then add the jinja reference
                    db['OWNER'] = self.create_jinja_role_instance(db['OWNER'])
                
                tags = []
                tags_sans_jinja = []
                #tags_raw = self._sf.tag_references_get(db['DATABASE_NAME'], db['DATABASE_NAME'], 'database')
                tags_raw = tag_dict[db['DATABASE_NAME']]
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
                db['TAGS'] = tags
                db['TAGS_SANS_JINJA'] = tags_sans_jinja
                
                #grants_raw = self._sf.grants_get(db['DATABASE_NAME'], 'database')
                grants_raw = grant_dict[db['DATABASE_NAME']]
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
                db['GRANTS_SANS_JINJA'] = grants_combined_sans_jinja
                db['GRANTS'] = grants_combined

                data.append(db)      

    return data   
