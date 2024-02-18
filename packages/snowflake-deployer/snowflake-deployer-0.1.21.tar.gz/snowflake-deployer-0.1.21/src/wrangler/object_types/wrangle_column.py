##########################################################################
##########################################################################
##########################################################################
# NO LONGER USED - WRAPPED INTO OBJECT
##########################################################################
##########################################################################
##########################################################################
from src.util.util import remove_prefix
import json

def wrangle_column(self, database_name:str, schema_name:str, object_name:str, env_database_prefix:str, deploy_db_name:str, ignore_roles_list:str, deploy_tag_list:list[str], current_role:str, available_roles:list[str], handle_ownership, semaphore)->dict:
    if env_database_prefix is None:
        env_database_prefix = ''

    cols = self._sf.columns_get(database_name, schema_name, object_name)  
    
    data = []
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

        data.append(c)
    
    return data   
