from src.util.util import remove_prefix
import threading
from time import sleep

def _get_child_roles(self_sf, semaphore, parent_role:str, role_dict:dict):
    with semaphore:
        child_grants_raw = self_sf._sf.role_child_grants_get(parent_role)
        role_dict[parent_role] = child_grants_raw

def _get_tag_references(self_sf, semaphore, parent_role:str, tag_dict:dict):
    with semaphore:
        tags_raw = self_sf._sf.tag_references_get('SNOWFLAKE', parent_role, 'role')
        tag_dict[parent_role] = tags_raw

def wrangle_role(self, env_role_prefix:str, env_database_prefix:str, deploy_db_name:str, ignore_roles_list:str, deploy_tag_list:list[str], current_role:str, available_roles:list[str], handle_ownership, semaphore)->dict:
    if env_database_prefix is None:
        env_database_prefix = ''
    if env_role_prefix is None:
        env_role_prefix = ''

    roles = self._sf.roles_get(env_role_prefix)  
    #print(roles)
    # Get tags & grants async for performce
    threads_all = []
    tag_dict = {}
    role_dict = {}
    for r in roles:
        parent_role = r['ROLE_NAME']

        # async get all role grants
        thread_name = 'grants_'+parent_role
        t = threading.Thread(target=_get_child_roles, name=thread_name, args=(self, semaphore, parent_role, role_dict))
        threads_all.append(t)

        # async get all tag grants
        thread_name = 'tags_'+parent_role
        t = threading.Thread(target=_get_tag_references, name=thread_name, args=(self, semaphore, parent_role, tag_dict))
        threads_all.append(t)

    # async management
    for t in threads_all:
        t.start()
    for t in threads_all:
        t.join()

    #while len(threading.enumerate()) > 1:
    #    sleep(1)

    data = []
    for r in roles:
        if r['ROLE_NAME'] not in ignore_roles_list:
            r['ROLE_NAME_SANS_ENV'] = remove_prefix(r['ROLE_NAME'],env_role_prefix)
            
            r['OWNER_SANS_JINJA'] = r['OWNER']
            r['OWNER'] = self._handle_ownership(handle_ownership, r['OWNER'], 'role', r['ROLE_NAME'], current_role, available_roles)
            
            if r['OWNER'] not in ignore_roles_list: # if role managed by deployer (not out of the box) then add the jinja reference
                r['OWNER'] = self.create_jinja_role_instance(r['OWNER'])
            
            #parent_grants = []
            #parent_grants_raw = self._sf.role_parent_grants_get(r['ROLE_NAME'])
            #for parent_grant_raw in parent_grants_raw:
            #    parent_grant_sans_prefix = remove_prefix(parent_grant_raw, env_role_prefix)
            #    if parent_grant_sans_prefix not in ignore_roles_list:
            #        parent_grant = self.create_jinja_role_instance(parent_grant_sans_prefix)
            #    else:
            #        parent_grant = parent_grant_sans_prefix
            #    parent_grants.append(parent_grant)
            #r['PARENT_GRANTS'] = parent_grants
            child_grants = []
            #child_grants_raw = self._sf.role_child_grants_get(r['ROLE_NAME']) # JUST REMOVED THIS
            child_grants_raw = role_dict[r['ROLE_NAME']]

            #print('#### RAW ####')
            #print(child_grants_raw)
            for child_grant_raw in child_grants_raw:
                child_grant_sans_prefix = remove_prefix(child_grant_raw, env_role_prefix)
                if child_grant_sans_prefix not in ignore_roles_list:
                    child_grant = self.create_jinja_role_instance(child_grant_sans_prefix)
                else:
                    child_grant = child_grant_sans_prefix
                child_grants.append(child_grant)
            r['CHILD_ROLES'] = child_grants
            r['CHILD_ROLES_SANS_JINJA'] = child_grants_raw
            #print('#### MODIFIED ####')
            #print(child_grants)

            tags = []
            tags_sans_jinja = []
            #tags_raw = self._sf.tag_references_get('SNOWFLAKE', r['ROLE_NAME'], 'role') #warehouse tag references live within Snowflake db
            tags_raw = tag_dict[r['ROLE_NAME']]
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
            r['TAGS'] = tags
            r['TAGS_SANS_JINJA'] = tags_sans_jinja

            data.append(r)
        
    return data   
