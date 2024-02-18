def deploy_masking_policy(self, policy_full_name:str, file_hash:str, file_hash_code:str, config:dict, body_code:str, object_state_dict:dict, db_hash_dict:dict, db_masking_policy:dict)->str:
    # policy_full_name = <db>.<schema>.<name>
    #SIGNATURE:list, RETURN_TYPE:str, EXEMPT_OTHER_POLICIES:bool, OWNER:str, COMMENT:str, BODY:str, TAGS:list, GRANTS:list, DEPLOY_ROLE:str
    #SIGNATURE, RETURN_TYPE, EXEMPT_OTHER_POLICIES, OWNER, COMMENT, BODY, TAGS, GRANTS, DEPLOY_ROLE
    # Get vars from config
    SIGNATURE = config['SIGNATURE'] if 'SIGNATURE' in config and config['SIGNATURE'] != '' and config['SIGNATURE'] is not None else []
    RETURN_TYPE = config['RETURN_TYPE'] if 'RETURN_TYPE' in config else None
    EXEMPT_OTHER_POLICIES = config['EXEMPT_OTHER_POLICIES'] if 'EXEMPT_OTHER_POLICIES' in config else None
    OWNER = config['OWNER'] if 'OWNER' in config else None
    COMMENT = config['COMMENT'] if 'COMMENT' in config else None

    TAGS = config['TAGS'] if 'TAGS' in config and config['TAGS'] != '' and config['TAGS'] is not None else []
    BODY = body_code
    GRANTS = config['GRANTS'] if 'GRANTS' in config and config['GRANTS'] != '' and config['GRANTS'] is not None else []
    ENVS = config['DEPLOY_ENV'] if 'DEPLOY_ENV' in config else None

    if ENVS is not None and self._deploy_env not in ENVS:
        return_status = 'E'
    else:
        # Check if db exists 

        #policy_exists, sf_owner = self._sf.masking_policy_check_exists(policy_full_name)
        if policy_full_name in db_hash_dict:
            policy_exists = True
            sf_owner = db_hash_dict[policy_full_name]['owner']
            db_hash = db_hash_dict[policy_full_name]['db_hash']
        else:
            policy_exists = False
            sf_owner = ''
            db_hash = ''

        if policy_full_name in object_state_dict and object_state_dict[policy_full_name]['OBJECT_TYPE'].upper() == 'MASKING_POLICY':
            state_file_hash = object_state_dict[policy_full_name]['DEPLOY_HASH']
            state_db_hash = object_state_dict[policy_full_name]['DB_HASH']
            state_file_hash_code = object_state_dict[policy_full_name]['DEPLOY_HASH_CODE']
        else:
            state_file_hash = ''
            state_db_hash = ''
            state_file_hash_code = ''

        #print('************************************')
        #print(state_file_hash)
        #print(file_hash)
        #print(state_file_hash_code)
        #print(file_hash_code)
        #print(state_db_hash)
        #print(db_hash)
        #print('************************************')

        if not policy_exists:
            # Create database
            self._sf.masking_policy_create(policy_full_name, SIGNATURE, RETURN_TYPE, EXEMPT_OTHER_POLICIES, OWNER, COMMENT, BODY, TAGS, GRANTS, self._deploy_role)

            db_hash_new = self._hasher.hash_masking_policy(SIGNATURE, RETURN_TYPE, EXEMPT_OTHER_POLICIES, OWNER, COMMENT, TAGS, BODY, GRANTS)
            self._sf.deploy_hash_apply(policy_full_name, 'MASKING_POLICY', file_hash, file_hash_code, db_hash_new, self._deploy_env, self._deploy_db_name)

            return_status = 'C'
        else:
            self._handle_ownership(sf_owner, 'masking policy', policy_full_name)

            # Get file hash from Snowflake & check if exist
            #sf_deploy_hash = self._sf.deploy_hash_get(self._deploy_db_name, policy_full_name, 'masking policy')
            #sf_deploy_code_hash = self._sf.deploy_code_hash_get(self._deploy_db_name, policy_full_name, 'masking policy')
            
            if state_file_hash != file_hash or state_file_hash_code != file_hash_code or state_db_hash != db_hash:
                tags_to_remove = list(filter(lambda x: x not in TAGS, db_masking_policy[policy_full_name]['TAGS_SANS_JINJA']))
                grants_to_remove = list(filter(lambda x: x not in GRANTS, db_masking_policy[policy_full_name]['GRANTS_SANS_JINJA']))
                
                self._sf.masking_policy_alter(policy_full_name, SIGNATURE, RETURN_TYPE, EXEMPT_OTHER_POLICIES, OWNER, COMMENT, BODY, TAGS, GRANTS, self._deploy_role, tags_to_remove, grants_to_remove)
                db_hash_new = self._hasher.hash_masking_policy(SIGNATURE, RETURN_TYPE, EXEMPT_OTHER_POLICIES, OWNER, COMMENT, TAGS, BODY, GRANTS)
                self._sf.deploy_hash_apply(policy_full_name, 'MASKING_POLICY', file_hash, file_hash_code, db_hash_new, self._deploy_env, self._deploy_db_name)
                
                return_status = 'U'
            else:
                return_status = 'I'
    return return_status