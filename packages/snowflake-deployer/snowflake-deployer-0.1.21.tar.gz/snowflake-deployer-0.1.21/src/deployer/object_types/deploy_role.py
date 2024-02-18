def deploy_role(self, role_name:str, file_hash:str, config:dict, object_state_dict:dict, db_hash_dict:dict, db_role:dict)->str:
    # warehouse_name in format <WAREHOUSE_NAME>
    
    # Get vars from config
    OWNER = config['OWNER'] if 'OWNER' in config else None
    COMMENT = config['COMMENT'] if 'COMMENT' in config else None
    CHILD_ROLES = config['CHILD_ROLES'] if 'CHILD_ROLES' in config else None
    TAGS = config['TAGS'] if 'TAGS' in config and config['TAGS'] != '' and config['TAGS'] is not None else []
    ENVS = config['DEPLOY_ENV'] if 'DEPLOY_ENV' in config else None

    #if OWNER is not None and type(OWNER) is not str:
    #    raise Exception('Invalid OWNER in YAML config - must be a string')
    #if COMMENT is not None and type(COMMENT) is not str:
    #    raise Exception('Invalid COMMENT in YAML config - must be a string')
    #if TAGS is not None and type(TAGS) is not list:
    #    raise Exception('Invalid TAGS in YAML config - must be a list')
    if ENVS is not None and self._deploy_env not in ENVS:
        return_status = 'E'
    else:
        # Check if db exists 
        #role_exists, sf_owner = self._sf.role_check_exists(role_name)
        if role_name in db_hash_dict:
            role_exists = True
            sf_owner = db_hash_dict[role_name]['owner']
            db_hash = db_hash_dict[role_name]['db_hash']
        else:
            role_exists = False
            sf_owner = ''
            db_hash = ''

        if role_name in object_state_dict and object_state_dict[role_name]['OBJECT_TYPE'].upper() == 'ROLE':
            state_file_hash = object_state_dict[role_name]['DEPLOY_HASH']
            state_db_hash = object_state_dict[role_name]['DB_HASH']
        else:
            state_file_hash = ''
            state_db_hash = ''

        #print('*****************************')
        #print(state_file_hash)
        #print(state_db_hash)
        #print(file_hash)
        #print(db_hash)
        #print('*****************************')

        if not role_exists:
            # Create database
            self._sf.role_create(role_name, OWNER, COMMENT, CHILD_ROLES, TAGS, self._deploy_role)
            db_hash_new = self._hasher.hash_role(OWNER, COMMENT, CHILD_ROLES, TAGS)
            self._sf.deploy_hash_apply(role_name, 'ROLE', file_hash, '', db_hash_new, self._deploy_env, self._deploy_db_name)

            #self._sf.deploy_hash_apply(role_name, file_hash, 'ROLE', self._deploy_db_name)
            return_status = 'C'
        else:
            self._handle_ownership(sf_owner, 'role', role_name)

            # Get file hash from Snowflake & check if exist
            #sf_deploy_hash = self._sf.deploy_hash_get(self._deploy_db_name, role_name, 'role')
            
            if state_file_hash != file_hash or state_db_hash != db_hash:
                tags_to_remove = list(filter(lambda x: x not in TAGS, db_role[role_name]['TAGS_SANS_JINJA']))
                grants_to_remove = list(filter(lambda x: x not in CHILD_ROLES, db_role[role_name]['CHILD_ROLES_SANS_JINJA']))
                
                self._sf.role_alter(role_name, OWNER, COMMENT, CHILD_ROLES, TAGS, tags_to_remove, grants_to_remove)
                db_hash_new = self._hasher.hash_role(OWNER, COMMENT, CHILD_ROLES, TAGS)
                self._sf.deploy_hash_apply(role_name, 'ROLE', file_hash, '', db_hash_new, self._deploy_env, self._deploy_db_name)

                return_status = 'U'
            else:
                # else - ignore - everything up to date if hashes match
                #print('Ignoring ' + role_name + ' - deploy_hash tag matches file hash')
                return_status = 'I'

    return return_status