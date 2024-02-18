from src.util.util import remove_prefix
import threading
from time import sleep

def _get_grants(self_sf, semaphore, warehouse_name:str, grant_dict:dict):
    with semaphore:
        grants_raw = self_sf._sf.grants_get(warehouse_name, 'warehouse')
        grant_dict[warehouse_name] = grants_raw

def _get_tag_references(self_sf, semaphore, warehouse_name:str, tag_dict:dict):
    with semaphore:
        tags_raw = self_sf._sf.tag_references_get('SNOWFLAKE', warehouse_name, 'warehouse')
        tag_dict[warehouse_name] = tags_raw

def wrangle_warehouse(self, env_warehouse_prefix:str, env_database_prefix:str, env_role_prefix:str, deploy_db_name:str, ignore_roles_list:str, deploy_tag_list:list[str], current_role:str, available_roles:list[str], handle_ownership, semaphore)->dict:
    if env_database_prefix is None:
        env_database_prefix = ''
    if env_warehouse_prefix is None:
        env_warehouse_prefix = ''
    if env_role_prefix is None:
        env_role_prefix = ''

    whs = self._sf.warehouses_get(env_warehouse_prefix)  
    
    # Get tags & grants async for performce
    threads_all = []
    tag_dict = {}
    grant_dict = {}
    for wh in whs:
        warehouse_name = wh['WAREHOUSE_NAME']

        # async get all role grants
        thread_name = 'whgrants_'+warehouse_name
        t = threading.Thread(target=_get_grants, name=thread_name, args=(self, semaphore, warehouse_name, grant_dict))
        threads_all.append(t)

        # async get all tag grants
        thread_name = 'whtags_'+warehouse_name
        t = threading.Thread(target=_get_tag_references, name=thread_name, args=(self, semaphore, warehouse_name, tag_dict))
        threads_all.append(t)

    # async management
    for t in threads_all:
        t.start()
    for t in threads_all:
        t.join()

    #while len(threading.enumerate()) > 1:
    #    sleep(1)

    data = []
    for wh in whs:
        wh['WAREHOUSE_NAME_SANS_ENV'] = remove_prefix(wh['WAREHOUSE_NAME'],env_warehouse_prefix)
        wh['WAREHOUSE_SIZE'] = wh['WAREHOUSE_SIZE'].replace('-','').upper()
        
        wh['OWNER_SANS_JINJA'] = wh['OWNER']
        wh['OWNER'] = self._handle_ownership(handle_ownership, wh['OWNER'], 'warehouse', wh['WAREHOUSE_NAME'], current_role, available_roles)
        
        if wh['OWNER'] not in ignore_roles_list: # if role managed by deployer (not out of the box) then add the jinja reference
            wh['OWNER'] = self.create_jinja_role_instance(wh['OWNER'])
        
        tags = []
        tags_sans_jinja = []
        #tags_raw = self._sf.tag_references_get('SNOWFLAKE', wh['WAREHOUSE_NAME'], 'warehouse') #warehouse tag references live within Snowflake db
        tags_raw = tag_dict[wh['WAREHOUSE_NAME']]
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
        wh['TAGS'] = tags
        wh['TAGS_SANS_JINJA'] = tags_sans_jinja
        
        #grants_raw = self._sf.grants_get(wh['WAREHOUSE_NAME'], 'warehouse')
        grants_raw = grant_dict[wh['WAREHOUSE_NAME']]
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
        #combine grants with delimiter
        grants_combined = self._combine_grants(grants)
        grants_combined_sans_jinja = self._combine_grants(grants_sans_jinja)
        wh['GRANTS_SANS_JINJA'] = grants_combined_sans_jinja
        wh['GRANTS'] = grants_combined

        data.append(wh)
    
    return data   
