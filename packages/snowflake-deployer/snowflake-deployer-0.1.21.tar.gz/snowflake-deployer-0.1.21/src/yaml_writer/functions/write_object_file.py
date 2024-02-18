from pathlib import Path
import yaml
#import ruamel.yaml
import src.common.processing_vars as var
def write_object_file(self,database_name:str, schema_name:str, d: dict, object_metadata_only: bool, override_existing_tags: bool=True):
    yml_path = 'snowflake/data/' + database_name + '/' + schema_name + '/OBJECTS/' + database_name + '__' + schema_name + '__' + d['OBJECT_NAME'] + '.yml'
    
    data = self.create_parent_load_data(yml_path)
    #print('$$$$$$$$$$$ file data $$$$$$$$$$$')
    #print(data)
    #print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    data['OBJECT_TYPE']=self.choose_value_string(data, 'OBJECT_TYPE', d,'OBJECT_TYPE', var.EMPTY_STRING)
    data['COMMENT']=self.choose_value_string(data, 'COMMENT', d,'COMMENT', var.EMPTY_STRING)
    data['OWNER']=self.choose_value_string(data, 'OWNER', d,'OWNER', var.EMPTY_STRING)
    data['RETENTION_TIME_IN_DAYS'] = self.choose_value_string(data, 'RETENTION_TIME_IN_DAYS', d,'RETENTION_TIME_IN_DAYS', var.EMPTY_STRING)
    

    if 'ROW_ACCESS_POLICY' in d and d['ROW_ACCESS_POLICY'] != {}:
        row_policy_jinjafied = {}
        row_policy_jinjafied['NAME'] = self.convert_for_yaml_write(d['ROW_ACCESS_POLICY']['NAME'])
        row_policy_jinjafied['INPUT_COLUMNS'] = d['ROW_ACCESS_POLICY']['INPUT_COLUMNS'] 
        data['ROW_ACCESS_POLICY'] = row_policy_jinjafied
    elif 'ROW_ACCESS_POLICY' in data and data['ROW_ACCESS_POLICY'] != {}:
        data['ROW_ACCESS_POLICY'] = data['ROW_ACCESS_POLICY']
    else:
        data['ROW_ACCESS_POLICY'] = {}

    if ('TAGS' in d and d['TAGS'] != []):
        #if not override_existing_tags and 'TAGS' in data:
        #    # first grab file tags and then override with tags passed in
        #    tmp_tags = data['TAGS']
        #    for k in d['TAGS'].keys():
        #        tmp_tags[k] = d['TAGS'][k]
        #    d['TAGS'] = tmp_tags

        if 'TAGS' in data:
            data['TAGS'] = self.choose_list_objects_file_trumps(d['TAGS'], data['TAGS'])
        else:
            data['TAGS'] = d['TAGS']
    elif ('TAGS' in data and data['TAGS'] != [] and data['TAGS'] is not None):
        data['TAGS'] = data['TAGS']
    else:
        data['TAGS']=var.EMPTY_STRING

    if ('GRANTS' in d and d['GRANTS'] != []):
        if 'GRANTS' in data:
            data['GRANTS'] = self.choose_list_objects(d['GRANTS'], data['GRANTS'])
        else:
            data['GRANTS'] = d['GRANTS']
    elif ('GRANTS' in data and data['GRANTS'] != [] and data['GRANTS'] is not None):
        data['GRANTS'] = data['GRANTS']
    else:
        data['GRANTS']=var.EMPTY_STRING

    #data['COLUMNS'] = self.choose_list_objects(d['COLUMNS'], data['COLUMNS'])
    #data['COLUMNS'] = d['COLUMNS']
    new_cols = []
    if 'COLUMNS' in d and 'COLUMNS' in data:
        #print(data['COLUMNS'])
        for col in d['COLUMNS']:
            tmp_col = {}
            col_name = col['NAME']
            tmp_col['NAME'] = col_name
            if 'TAGS' in col:
                input_tags = col['TAGS']
                file_tags = []
                for file_col in data['COLUMNS']:
                    #print(file_col)
                    if col_name == file_col['NAME']:
                        file_tags = file_col['TAGS']
                        break
                
                if not override_existing_tags:
                    new_tags = self.choose_list_objects_file_trumps(input_tags, file_tags)
                else:
                    new_tags = self.choose_list_objects(input_tags, file_tags)

                if 'TAGS_TO_REMOVE' in col:
                    for tag_to_remove in col['TAGS_TO_REMOVE']:
                        for tag in new_tags:
                            if tag_to_remove in tag.keys():
                                new_tags.remove(tag)
                tmp_col['TAGS'] = new_tags

            new_cols.append(tmp_col)

        data['COLUMNS'] = new_cols
    elif 'COLUMNS' in d:
        for col in d['COLUMNS']:
            tmp_col = {}
            tmp_col['NAME'] = col['NAME'] if 'NAME' in col else []
            tmp_col['TAGS'] = col['TAGS'] if 'TAGS' in col else []
            new_cols.append(tmp_col)
        data['COLUMNS'] = new_cols
        
    #if 'RENAME' in data:
    #    del data['RENAME']

    #ryaml = ruamel.yaml.YAML(typ=['rt', 'string'])
    #yaml_string = ryaml.dump_to_string(data)
    yaml_string = yaml.dump(data, sort_keys=False)
    #yaml_string_converted = self.replace_jinja_ref_string(yaml_string)
    #yaml_string_converted = yaml_string_converted.replace("'"+var.EMPTY_STRING+"'",'')
    yaml_string_converted = self.convert_special_characters_back_in_file(yaml_string)
    
    with open(yml_path, "w+") as f:
        f.write(yaml_string_converted)

    #with Path(yml_path).open("w", encoding="utf-8") as f:
    #    yaml.dump(data,f,default_style=None,default_flow_style=False, sort_keys=False)
    #    #f.write('#RENAME: #uncomment with new name to rename')

    


