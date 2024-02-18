from src.util.util import remove_prefix
import threading
from time import sleep

def _get_grants(self_sf, full_policy_name:str, grant_dict:dict):
    grants_raw = self_sf._sf.grants_get(full_policy_name, 'row access policy')
    grant_dict[full_policy_name] = grants_raw

def _get_tag_references(self_sf, database_name:str, full_policy_name:str, tag_dict:dict):
    tags_raw = self_sf._sf.tag_references_get(database_name, full_policy_name, 'row access policy') 
    tag_dict[full_policy_name] = tags_raw

def wrangle_row_access_policy(self, database_name:str, schema_name:str, env_database_prefix:str, env_role_prefix:str, deploy_db_name:str, ignore_roles_list:str, deploy_tag_list:list[str], current_role:str, available_roles:list[str], handle_ownership, semaphore)->dict:
    if env_database_prefix is None:
        env_database_prefix = ''
    if env_role_prefix is None:
        env_role_prefix = ''

    policies = self._sf.row_access_policies_get(database_name, schema_name)  
    
    # Get tags & grants async for performce
    threads_all = []
    tag_dict = {}
    grant_dict = {}
    for d in policies:
        full_policy_name = database_name + '.' + schema_name + '.' + d['ROW_ACCESS_POLICY_NAME'].replace(' ','')

        # async get all role grants
        _get_grants(self, full_policy_name, grant_dict)
        #thread_name = 'grants_'+full_policy_name
        #t = threading.Thread(target=_get_grants, name=thread_name, args=(self, semaphore, full_policy_name, grant_dict))
        #threads_all.append(t)

        # async get all tag grants
        _get_tag_references(self, database_name, full_policy_name, tag_dict)
        #thread_name = 'tags_'+full_policy_name
        #t = threading.Thread(target=_get_tag_references, name=thread_name, args=(self, semaphore, database_name, full_policy_name, tag_dict))
        #threads_all.append(t)

    # async management
    #for t in threads_all:
    #    t.start()
    #for t in threads_all:
    #    t.join()

    #while len(threading.enumerate()) > 1:
    #    sleep(1)

    data = []
    for d in policies:
        full_policy_name = database_name + '.' + schema_name + '.' + d['ROW_ACCESS_POLICY_NAME'].replace(' ','')
        d['FULL_POLICY_NAME'] = full_policy_name
        d['OWNER_SANS_JINJA'] = d['OWNER']
        d['OWNER'] = self._handle_ownership(handle_ownership, d['OWNER'], 'row access policy', full_policy_name, current_role, available_roles)

        if d['OWNER'] not in ignore_roles_list: # if role managed by deployer (not out of the box) then add the jinja reference
            d['OWNER'] = self.create_jinja_role_instance(d['OWNER'])
        
        tags = []
        tags_sans_jinja = []
        #tags_raw = self._sf.tag_references_get(database_name, full_policy_name, 'row access policy') #task tag references live within Snowflake db
        tags_raw = tag_dict[full_policy_name]
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
        d['TAGS'] = tags
        d['TAGS_SANS_JINJA'] = tags_sans_jinja

        #grants_raw = self._sf.grants_get(full_policy_name, 'row access policy')
        grants_raw = grant_dict[full_policy_name]
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
        d['GRANTS_SANS_JINJA'] = grants_combined_sans_jinja
        d['GRANTS'] = grants_combined

        data.append(d)
    
    return data   
