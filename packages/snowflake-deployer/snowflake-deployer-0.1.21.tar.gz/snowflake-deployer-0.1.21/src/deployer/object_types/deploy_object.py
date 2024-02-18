from src.common.exceptions import feature_not_supported
def deploy_object(self, object_name:str, file_hash:str, config:dict, object_state_dict:dict, db_hash_dict:dict, db_object:dict)->str:
    # object_name in format <DATABASE_NAME>.<SCHEMA_NAME>.<OBJECT_NAME> 
    # THIS CAN BE A TABLE OR VIEW!!!
    
    # Get vars from config
    DATA_RETENTION_TIME_IN_DAYS = int(config['DATA_RETENTION_TIME_IN_DAYS']) if 'DATA_RETENTION_TIME_IN_DAYS' in config else None 
    COMMENT = config['COMMENT'] if 'COMMENT' in config else None
    OWNER = config['OWNER'] if 'OWNER' in config else None
    CHANGE_TRACKING = config['CHANGE_TRACKING'] if 'CHANGE_TRACKING' in config else None
    TAGS = config['TAGS'] if 'TAGS' in config and config['TAGS'] != '' and config['TAGS'] is not None else []
    COLUMNS = config['COLUMNS'] if 'COLUMNS' in config and config['COLUMNS'] != '' and config['COLUMNS'] is not None else []
    GRANTS = config['GRANTS'] if 'GRANTS' in config and config['GRANTS'] != '' and config['GRANTS'] is not None else []
    ENVS = config['DEPLOY_ENV'] if 'DEPLOY_ENV' in config else None
    ROW_ACCESS_POLICY = config['ROW_ACCESS_POLICY'] if 'ROW_ACCESS_POLICY' in config else None
    #ROW_ACCESS_POLICY_COLUMNS = config['ROW_ACCESS_POLICY_COLUMNS'] if 'ROW_ACCESS_POLICY_COLUMNS' in config and config['ROW_ACCESS_POLICY_COLUMNS'] != '' and config['ROW_ACCESS_POLICY_COLUMNS'] is not None else []
    if ROW_ACCESS_POLICY is not None and ROW_ACCESS_POLICY != {}:
        if 'NAME' not in ROW_ACCESS_POLICY:
            raise Exception('Invalid ROW_ACCESS_POLICY in YAML config - must include NAME if deploying a row access policy')
        if 'INPUT_COLUMNS' not in ROW_ACCESS_POLICY:
            raise Exception('Invalid ROW_ACCESS_POLICY in YAML config - must include INPUT_COLUMNS (list) if deploying a row access policy')
        if( type(ROW_ACCESS_POLICY['INPUT_COLUMNS']) != list ):
            raise Exception('Invalid ROW_ACCESS_POLICY in YAML config - NPUT_COLUMNS must be a LIST of columns to input to policy')
    
    
    #if DATA_RETENTION_TIME_IN_DAYS is not None and type(DATA_RETENTION_TIME_IN_DAYS) is not int:
    #    raise Exception('Invalid DATA_RETENTION_TIME_IN_DAYS in YAML config - must be a int')
    #if COMMENT is not None and type(COMMENT) is not str:
    #    raise Exception('Invalid COMMENT in YAML config - must be a string')
    #if OWNER is not None and type(OWNER) is not str:
    #    raise Exception('Invalid OWNER in YAML config - must be a string')
    #if CHANGE_TRACKING is not None and type(CHANGE_TRACKING) is not bool:
    #    raise Exception('Invalid CHANGE_TRACKING in YAML config - must be a boolean')
    #if TAGS is not None and type(TAGS) is not list:
    #    raise Exception('Invalid TAGS in YAML config - must be a list')
    #if COLUMNS is not None and type(COLUMNS) is not list:
    #    raise Exception('Invalid COLUMNS in YAML config - must be a list')
    #if ROW_ACCESS_POLICY is not None and ROW_ACCESS_POLICY != '':
    #    if ROW_ACCESS_POLICY_COLUMNS is None or ROW_ACCESS_POLICY_COLUMNS == []:
    #        raise Exception('Must include ROW_ACCESS_POLICY_COLUMNS if ROW_ACCESS_POLICY included')
    if ENVS is not None and self._deploy_env not in ENVS:
        return_status = 'E'
    else: 
        # Check if schema exists 
        #object_exists, sf_owner, last_ddl = self._sf.object_check_exists(object_name)
        if object_name in db_hash_dict:
            object_exists = True
            sf_owner = db_hash_dict[object_name]['owner']
            db_hash = db_hash_dict[object_name]['db_hash']
            #last_ddl = db_hash_dict[object_name]['last_ddl']
        else:
            object_exists = False
            sf_owner = ''
            db_hash = ''
            #last_ddl = ''
            
        if object_name in object_state_dict and object_state_dict[object_name]['OBJECT_TYPE'].upper() == 'OBJECT':
            state_file_hash = object_state_dict[object_name]['DEPLOY_HASH']
            state_db_hash = object_state_dict[object_name]['DB_HASH']
        else:
            state_file_hash = ''
            state_db_hash = ''

        #print('************************************')
        #print(object_state_dict)
        #print('************************************')
        #print(object_name)
        #print(state_file_hash)
        #print(file_hash)
        #print(state_db_hash)
        #print(db_hash)
        #print('************************************')

        if not object_exists:
            # Create Object
            #raise feature_not_supported('object', 'create new object')
            print('Ignoring object: ' + object_name + '; Object does not exist')
            #self._sf.schema_create(object_name, DATA_RETENTION_TIME_IN_DAYS, COMMENT, OWNER, TAGS)
            #self._sf.deploy_hash_apply(object_name, file_hash, 'SCHEMA', deploy_db_name)
            return_status = 'I'
            #return_status = 'C'
        else:
            self._handle_ownership(sf_owner, 'table', object_name)

            #print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
            #print(db_object[object_name]['TAGS_SANS_JINJA'])
            #print(TAGS)
            #print(db_object[object_name]['GRANTS_SANS_JINJA'])
            #print(GRANTS)

            #lst_file = [{'DEMO_CONTROL.GOVERNANCE.ENV': 'demo'}]
            #lst_db = [{'DEMO_CONTROL.GOVERNANCE.ENV': 'demo'}, {'DEMO_CONTROL.GOVERNANCE.ENV2': 'demo2'}]
            #lst_diff = set(lst1) - set(lst2)
            
            # Get file hash from Snowflake & check if exist
            #sf_deploy_hash, sf_last_update = self._sf.deploy_hash_and_last_update_get(self._deploy_db_name, object_name, 'table')
            
            #if sf_deploy_hash != file_hash or last_ddl > sf_last_update:
            if state_file_hash != file_hash or state_db_hash != db_hash:
                
                tags_to_remove = list(filter(lambda x: x not in TAGS, db_object[object_name]['TAGS_SANS_JINJA']))
                #print(tags_to_remove)
                grants_to_remove = list(filter(lambda x: x not in GRANTS, db_object[object_name]['GRANTS_SANS_JINJA']))
                #print(grants_to_remove)
                
                self._sf.object_alter(object_name, DATA_RETENTION_TIME_IN_DAYS, COMMENT, OWNER, CHANGE_TRACKING, ROW_ACCESS_POLICY, TAGS, GRANTS, tags_to_remove, grants_to_remove)
                

                # Create column map
                db_col_map = {}
                for col in db_object[object_name]['COLUMNS']:
                    db_col_map[col['NAME']] = col['TAGS_SANS_JINJA']

                for column in COLUMNS:
                    
                    column_tags_to_remove = list(filter(lambda x: x not in column['TAGS'], db_col_map[column['NAME']]))
                
                    if 'TAGS' in column or column_tags_to_remove is not None or column_tags_to_remove != []: # only update column if something exists to update
                        self._sf.column_alter(object_name, column['NAME'], column['TAGS'], column_tags_to_remove)
                
                db_hash_new = self._hasher.hash_object(DATA_RETENTION_TIME_IN_DAYS, COMMENT, OWNER, CHANGE_TRACKING, TAGS, COLUMNS, GRANTS, ROW_ACCESS_POLICY)
                self._sf.deploy_hash_apply(object_name, 'OBJECT', file_hash, '', db_hash_new, self._deploy_env, self._deploy_db_name)
        
                return_status = 'U'
            else:
                # else - ignore - everything up to date if hashes match
                #print('Ignoring ' + object_name + ' - deploy_hash tag matches file hash')

                return_status = 'I'
    return return_status