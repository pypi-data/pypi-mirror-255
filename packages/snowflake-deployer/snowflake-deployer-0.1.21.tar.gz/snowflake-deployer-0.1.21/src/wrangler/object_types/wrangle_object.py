from src.util.util import remove_prefix
import threading
from time import sleep
import json

def _get_grants(self_sf, object_name_with_db_schema:str, grant_dict:dict):
    grants_raw = self_sf._sf.grants_get(object_name_with_db_schema, 'table')
    grant_dict[object_name_with_db_schema] = grants_raw

def _get_tag_references(self_sf, database_name:str, object_name_with_db_schema:str, object_type:str, tag_dict:dict):
    tags_raw = self_sf._sf.tag_references_get(database_name, object_name_with_db_schema, object_type)
    tag_dict[object_name_with_db_schema] = tags_raw

def _get_row_access_policies(self_sf, object_name_with_db_schema:str, row_access_policy_dict:dict):
    row_access_policy = self_sf._sf.object_row_access_policy_reference(object_name_with_db_schema)
    row_access_policy_dict[object_name_with_db_schema] = row_access_policy

def _get_columns(self_sf, object_name_with_db_schema, database_name, schema_name, object_name, columns_dict):
    cols = self_sf._sf.columns_get(database_name, schema_name, object_name)  
    columns_dict[object_name_with_db_schema] = cols if cols is not None else []

def wrangle_object(self, database_name:str, schema_name:str, env_database_prefix:str, env_role_prefix:str, deploy_db_name:str, ignore_roles_list:str, deploy_tag_list:list[str], current_role:str, available_roles:list[str], handle_ownership, semaphore)->dict:
    # database_name should include any db prefixes
    if env_database_prefix is None:
        env_database_prefix = ''
    if env_role_prefix is None:
        env_role_prefix = ''

    objects = self._sf.objects_get(database_name, schema_name)  

    # Get tags & grants & row access policies async for performce
    threads_all = []
    grant_dict = {}
    tag_dict = {}
    columns_dict = {}
    row_access_policy_dict = {}
    for o in objects:
        object_name_with_db_schema = database_name + '.' + schema_name + '.' + o['OBJECT_NAME']
        
        # async get all role grants
        _get_grants(self, object_name_with_db_schema, grant_dict)
        #thread_name = 'grants_'+object_name_with_db_schema
        #t = threading.Thread(target=_get_grants, name=thread_name, args=(self, semaphore, object_name_with_db_schema, grant_dict))
        #threads_all.append(t)

        # async get all tag grants
        _get_tag_references(self, database_name, object_name_with_db_schema, o['OBJECT_TYPE'], tag_dict)
        #thread_name = 'tags_'+object_name_with_db_schema
        #t = threading.Thread(target=_get_tag_references, name=thread_name, args=(self, semaphore, database_name, object_name_with_db_schema,o['OBJECT_TYPE'], tag_dict))
        #threads_all.append(t)
        
        # Row access policies for each table 
        _get_row_access_policies(self, object_name_with_db_schema, row_access_policy_dict)
        #thread_name = 'row_access_policy_'+object_name_with_db_schema
        #t = threading.Thread(target=_get_row_access_policies, name=thread_name, args=(self, semaphore, object_name_with_db_schema, row_access_policy_dict))
        #threads_all.append(t)
        
        # Columns
        _get_columns(self, object_name_with_db_schema, database_name, schema_name, o['OBJECT_NAME'], columns_dict)
        #thread_name = 'columns_'+object_name_with_db_schema
        #t = threading.Thread(target=_get_columns, name=thread_name, args=(self, semaphore, object_name_with_db_schema, database_name, schema_name, o['OBJECT_NAME'], columns_dict))
        #threads_all.append(t)

    # async management
    #for t in threads_all:
    #    t.start()
    #for t in threads_all:
    #    t.join()

    #while len(threading.enumerate()) > 1:
    #    sleep(1)

    

    data = []
    for o in objects:
        object_name_with_db_schema = database_name + '.' + schema_name + '.' + o['OBJECT_NAME']
        o['FULL_OBJECT_NAME'] = object_name_with_db_schema
        o['OWNER_SANS_JINJA'] = o['OWNER']
        o['OWNER'] = self._handle_ownership(handle_ownership, o['OWNER'], 'table', object_name_with_db_schema, current_role, available_roles)

        if o['OWNER'] not in ignore_roles_list: # if role managed by deployer (not out of the box) then add the jinja reference
            o['OWNER'] = self.create_jinja_role_instance(o['OWNER'])
        
        #print(row_access_policy_dict)
        #print(object_name_with_db_schema)

        # Get row access policies associated with an object
        #row_access_policy = self._sf.object_row_access_policy_reference(object_name_with_db_schema)
        row_access_policy = row_access_policy_dict[object_name_with_db_schema]
        o['ROW_ACCESS_POLICY'] = {}
        if row_access_policy != {}:
            row_access_policy_db = remove_prefix(row_access_policy['POLICY_DB'],env_database_prefix)
            o['ROW_ACCESS_POLICY']['NAME'] = self.create_jinja_ref(row_access_policy_db, row_access_policy['POLICY_SCHEMA'], row_access_policy['POLICY_NAME'])
            o['ROW_ACCESS_POLICY']['INPUT_COLUMNS'] = row_access_policy['INPUT_COLUMNS_LIST']

        tags = []
        tags_sans_jinja = []
        #tags_raw = self._sf.tag_references_get(database_name, object_name_with_db_schema, o['OBJECT_TYPE'])
        tags_raw = tag_dict[object_name_with_db_schema]
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
        o['TAGS'] = tags
        o['TAGS_SANS_JINJA'] = tags_sans_jinja

        #grants_raw = self._sf.grants_get(object_name_with_db_schema, 'table')
        grants_raw = grant_dict[object_name_with_db_schema]
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
        o['GRANTS_SANS_JINJA'] = grants_combined_sans_jinja
        o['GRANTS'] = grants_combined
  
        cols = columns_dict[object_name_with_db_schema]
        new_cols = []
        #print('#@#@#@#@#@#@#@#@#@#@@#@')
        #print(cols)
        for c in cols:
            
            tag_list = json.loads(c['TAG_LIST']) if c['TAG_LIST'] is not None else []

            tags = []
            tags_sans_jinja = []
            for t in tag_list:  
                #TAG_DATABASE, TAG_SCHEMA, TAG_NAME, TAG_VALUE
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
            c['TAGS'] = tags
            c['TAGS_SANS_JINJA'] = tags_sans_jinja
            c.pop('TAG_LIST')
            new_cols.append(c)
        o['COLUMNS'] = new_cols

        #o.pop('OBJECT_TYPE')
        data.append(o)
    
    #print('#@#@#@#@#@#@#@#@#@#@@#@')
    #print(data)
    #print('#@#@#@#@#@#@#@#@#@#@@#@')
    return data   
