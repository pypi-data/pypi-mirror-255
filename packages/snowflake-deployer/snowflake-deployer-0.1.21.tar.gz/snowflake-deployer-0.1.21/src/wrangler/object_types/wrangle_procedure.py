from src.util.util import remove_prefix
import threading
from time import sleep

def _get_grants(self_sf, proc_full_name:str, grant_dict:dict):
    grants_raw = self_sf._sf.grants_get(proc_full_name, 'procedure')
    grant_dict[proc_full_name] = grants_raw

def _get_tag_references(self_sf, database_name:str, proc_full_name:str, tag_dict:dict):
    tags_raw = self_sf._sf.tag_references_get(database_name, proc_full_name, 'procedure') 
    tag_dict[proc_full_name] = tags_raw

def wrangle_procedure(self, database_name:str, env_procedure_prefix:str, env_database_prefix:str, env_role_prefix:str, deploy_db_name:str, ignore_roles_list:str, deploy_tag_list:list[str], current_role:str, available_roles:list[str], handle_ownership, semaphore)->dict:
    if env_database_prefix is None:
        env_database_prefix = ''
    if env_procedure_prefix is None:
        env_procedure_prefix = ''
    if env_role_prefix is None:
        env_role_prefix = ''

    procs = self._sf.procedures_get(database_name)  
    
    # Get tags & grants async for performce
    threads_all = []
    grant_dict = {}
    tag_dict = {}
    for p in procs:
        schema_name = p['SCHEMA_NAME']
        proc_full_name = database_name + '.' + schema_name + '.' + p['ARGUMENT_SIGNATURE_TO_MATCH'].replace(' ','')
        
        # async get all role grants
        _get_grants(self, proc_full_name, grant_dict)
        #thread_name = 'grants_'+proc_full_name
        #t = threading.Thread(target=_get_grants, name=thread_name, args=(self, semaphore, proc_full_name, grant_dict))
        #threads_all.append(t)

        # async get all tag grants
        _get_tag_references(self, database_name, proc_full_name, tag_dict)
        #thread_name = 'tags_'+proc_full_name
        #t = threading.Thread(target=_get_tag_references, name=thread_name, args=(self, semaphore, database_name, proc_full_name, tag_dict))
        #threads_all.append(t)

    # async management
    #for t in threads_all:
    #    t.start()
    #for t in threads_all:
    #    t.join()

    #while len(threading.enumerate()) > 1:
    #    sleep(1)

    data = []
    for p in procs:
        schema_name = p['SCHEMA_NAME']
        proc_full_name = database_name + '.' + schema_name + '.' + p['ARGUMENT_SIGNATURE_TO_MATCH'].replace(' ','')
        p['PROC_FULL_NAME'] = proc_full_name
        
        p['PROCEDURE_NAME_SANS_ENV'] = remove_prefix(p['PROCEDURE_NAME'],env_procedure_prefix)
        
        p['OWNER_SANS_JINJA'] = p['OWNER']
        p['OWNER'] = self._handle_ownership(handle_ownership, p['OWNER'], 'procedure', proc_full_name, current_role, available_roles)

        p['IS_SECURE'] = True if p['IS_SECURE'] == True or p['IS_SECURE'].upper() == 'Y' else False 
        if p['OWNER'] not in ignore_roles_list: # if role managed by deployer (not out of the box) then add the jinja reference
            p['OWNER'] = self.create_jinja_role_instance(p['OWNER'])

        tags = []
        tags_sans_jinja = []
        #tags_raw = self._sf.tag_references_get(database_name, proc_full_name, 'procedure') #warehouse tag references live within Snowflake db
        tags_raw = tag_dict[proc_full_name]
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
        p['TAGS'] = tags
        p['TAGS_SANS_JINJA'] = tags_sans_jinja

        #grants_raw = self._sf.grants_get(proc_full_name, 'procedure')
        grants_raw = grant_dict[proc_full_name]
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
        p['GRANTS_SANS_JINJA'] = grants_combined_sans_jinja
        p['GRANTS'] = grants_combined
        
        p.pop('ARGUMENT_SIGNATURE_TO_MATCH')
        data.append(p)
    
    return data   
