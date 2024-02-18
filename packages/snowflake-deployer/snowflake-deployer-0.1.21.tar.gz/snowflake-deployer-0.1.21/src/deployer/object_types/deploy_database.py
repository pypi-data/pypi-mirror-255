def deploy_database(self, database_name:str, file_hash:str, config, object_state_dict:dict, db_hash_dict:dict, db_database:dict)->str:
    
    # Get vars from config
    DATA_RETENTION_TIME_IN_DAYS = int(config['DATA_RETENTION_TIME_IN_DAYS']) if 'DATA_RETENTION_TIME_IN_DAYS' in config else None 
    COMMENT = config['COMMENT'] if 'COMMENT' in config else None
    OWNER = config['OWNER'] if 'OWNER' in config else None
    TAGS = config['TAGS'] if 'TAGS' in config and config['TAGS'] != '' and config['GRANTS'] is not None else []
    GRANTS = config['GRANTS'] if 'GRANTS' in config and config['GRANTS'] != '' and config['GRANTS'] is not None else []
    ENVS = config['DEPLOY_ENV'] if 'DEPLOY_ENV' in config else None
        
    # commenting this out and moving to the validator class
    #if DATA_RETENTION_TIME_IN_DAYS is not None and type(DATA_RETENTION_TIME_IN_DAYS) is not int:
    #    raise Exception('Invalid DATA_RETENTION_TIME_IN_DAYS in YAML config - must be a int')
    #if COMMENT is not None and type(COMMENT) is not str:
    #    raise Exception('Invalid COMMENT in YAML config - must be a string')
    #if OWNER is not None and type(OWNER) is not str:
    #    raise Exception('Invalid OWNER in YAML config - must be a string')
    #if TAGS is not None and type(TAGS) is not list:
    #    raise Exception('Invalid TAGS in YAML config - must be a list')

    # Check if db exists 
    if ENVS is not None and self._deploy_env not in ENVS:
        return_status = 'E'
    else: 
        #db_exists, sf_owner = self._sf.database_check_exists(database_name)
        if database_name in db_hash_dict:
            db_exists = True
            sf_owner = db_hash_dict[database_name]['owner']
            db_hash = db_hash_dict[database_name]['db_hash']
        else:
            db_exists = False
            sf_owner = ''
            db_hash = ''

        if database_name in object_state_dict and object_state_dict[database_name]['OBJECT_TYPE'].upper() == 'DATABASE':
            state_file_hash = object_state_dict[database_name]['DEPLOY_HASH']
            state_db_hash = object_state_dict[database_name]['DB_HASH']
        else:
            state_file_hash = ''
            state_db_hash = ''

        if not db_exists:
            # Create database
            self._sf.database_create(database_name, DATA_RETENTION_TIME_IN_DAYS, COMMENT, OWNER, TAGS, GRANTS, self._deploy_role)
            db_hash_new = self._hasher.hash_database(DATA_RETENTION_TIME_IN_DAYS, OWNER, COMMENT, TAGS, GRANTS)
            self._sf.deploy_hash_apply(database_name, 'DATABASE', file_hash, '', db_hash_new, self._deploy_env, self._deploy_db_name)

            return_status = 'C'
        else:
            self._handle_ownership(sf_owner, 'database', database_name)

            # Get file hash from Snowflake & check if exist
            #sf_deploy_hash = self._sf.deploy_hash_get(self._deploy_db_name, database_name, 'database')
            
            if state_file_hash != file_hash or state_db_hash != db_hash:

                tags_to_remove = list(filter(lambda x: x not in TAGS, db_database[database_name]['TAGS_SANS_JINJA']))
                grants_to_remove = list(filter(lambda x: x not in GRANTS, db_database[database_name]['GRANTS_SANS_JINJA']))
                
                self._sf.database_alter(database_name, DATA_RETENTION_TIME_IN_DAYS, COMMENT, OWNER, TAGS, GRANTS, tags_to_remove, grants_to_remove)
                db_hash_new = self._hasher.hash_database(DATA_RETENTION_TIME_IN_DAYS, OWNER, COMMENT, TAGS, GRANTS)
                self._sf.deploy_hash_apply(database_name, 'DATABASE', file_hash, '', db_hash_new, self._deploy_env, self._deploy_db_name)

                return_status = 'U'
            else:
                # else - ignore - everything up to date if hashes match
                #print('Ignoring ' + database_name + ' - deploy_hash tag matches file hash')

                return_status = 'I'

    return return_status