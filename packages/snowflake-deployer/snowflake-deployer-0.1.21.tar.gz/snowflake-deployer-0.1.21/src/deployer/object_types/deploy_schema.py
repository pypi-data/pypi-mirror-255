def deploy_schema(self, schema_name:str, file_hash:str, config:dict, object_state_dict:dict, db_hash_dict:dict, db_schema:dict)->str:
    # schema_name in format <DATABASE_NAME>.<SCHEMA_NAME>
    
    # Get vars from config
    DATA_RETENTION_TIME_IN_DAYS = int(config['DATA_RETENTION_TIME_IN_DAYS']) if 'DATA_RETENTION_TIME_IN_DAYS' in config else None 
    COMMENT = config['COMMENT'] if 'COMMENT' in config else None
    OWNER = config['OWNER'] if 'OWNER' in config else None
    TAGS = config['TAGS'] if 'TAGS' in config and config['TAGS'] != '' and config['TAGS'] is not None else []
    GRANTS = config['GRANTS'] if 'GRANTS' in config and config['GRANTS'] != '' and config['GRANTS'] is not None else []
    ENVS = config['DEPLOY_ENV'] if 'DEPLOY_ENV' in config else None

    FULL_SCHEMA_NAME = config['FULL_SCHEMA_NAME'] if 'FULL_SCHEMA_NAME' in config else None
    
    # commenting this out and moving to the validator class
    #if DATA_RETENTION_TIME_IN_DAYS is not None and type(DATA_RETENTION_TIME_IN_DAYS) is not int:
    #    raise Exception('Invalid DATA_RETENTION_TIME_IN_DAYS in YAML config - must be a int')
    #if COMMENT is not None and type(COMMENT) is not str:
    #    raise Exception('Invalid COMMENT in YAML config - must be a string')
    #if OWNER is not None and type(OWNER) is not str:
    #    raise Exception('Invalid OWNER in YAML config - must be a string')
    #if TAGS is not None and type(TAGS) is not list:
    #    raise Exception('Invalid TAGS in YAML config - must be a list')

    if ENVS is not None and self._deploy_env not in ENVS:
        return_status = 'E'
    else: 
        # Check if schema exists 
        #schema_exists, sf_owner = self._sf.schema_check_exists(schema_name)
        #print('%%%%%%%%%%%%%%' + schema_name + '%%%%%%%%%%%%%%')
        #print(db_hash_dict)
        #print(object_state_dict)
        #print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        if schema_name in db_hash_dict:
            schema_exists = True
            sf_owner = db_hash_dict[schema_name]['owner']
            db_hash = db_hash_dict[schema_name]['db_hash']
        else:
            schema_exists = False
            sf_owner = ''
            db_hash = ''
            
        if schema_name in object_state_dict and object_state_dict[schema_name]['OBJECT_TYPE'].upper() == 'SCHEMA':
            state_file_hash = object_state_dict[schema_name]['DEPLOY_HASH']
            state_db_hash = object_state_dict[schema_name]['DB_HASH']
        else:
            state_file_hash = ''
            state_db_hash = ''


        if not schema_exists:
            # Create Schema
            self._sf.schema_create(schema_name, DATA_RETENTION_TIME_IN_DAYS, COMMENT, OWNER, TAGS, GRANTS, self._deploy_role)
            db_hash_new = self._hasher.hash_schema(DATA_RETENTION_TIME_IN_DAYS, OWNER, COMMENT, TAGS, GRANTS)
            self._sf.deploy_hash_apply(schema_name, 'SCHEMA', file_hash, '', db_hash_new, self._deploy_env, self._deploy_db_name)

            return_status = 'C'
        else:
            self._handle_ownership(sf_owner, 'schema', schema_name)

            # Get file hash from Snowflake & check if exist
            #sf_deploy_hash = self._sf.deploy_hash_get(self._deploy_db_name, schema_name, 'schema')
            
            if state_file_hash != file_hash or state_db_hash != db_hash:
                tags_to_remove = list(filter(lambda x: x not in TAGS, db_schema[schema_name]['TAGS_SANS_JINJA']))
                grants_to_remove = list(filter(lambda x: x not in GRANTS, db_schema[schema_name]['GRANTS_SANS_JINJA']))
                
                self._sf.schema_alter(schema_name, DATA_RETENTION_TIME_IN_DAYS, COMMENT, OWNER, TAGS, GRANTS, tags_to_remove, grants_to_remove)
                db_hash_new = self._hasher.hash_schema(DATA_RETENTION_TIME_IN_DAYS, OWNER, COMMENT, TAGS, GRANTS)
                self._sf.deploy_hash_apply(schema_name, 'SCHEMA', file_hash, '', db_hash_new, self._deploy_env, self._deploy_db_name)
                
                return_status = 'U'
            else:
                # else - ignore - everything up to date if hashes match
                #print('Ignoring ' + schema_name + ' - deploy_hash tag matches file hash')
                return_status = 'I'

    return return_status
