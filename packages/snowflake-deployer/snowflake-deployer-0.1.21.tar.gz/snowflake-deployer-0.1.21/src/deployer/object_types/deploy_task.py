def deploy_task(self, task_full_name:str, file_hash:str, file_hash_code:str, config:dict, body_code:str, object_state_dict:dict, db_hash_dict:dict, db_schema:dict)->str:
    # task_full_name = <db>.<schema>.<name>
   
    # Get vars from config
    WAREHOUSE = config['WAREHOUSE'] if 'WAREHOUSE' in config else None
    SCHEDULE = config['SCHEDULE'] if 'SCHEDULE' in config else None
    ALLOW_OVERLAPPING_EXECUTION = config['ALLOW_OVERLAPPING_EXECUTION'] if 'ALLOW_OVERLAPPING_EXECUTION' in config else None
    ERROR_INTEGRATION = config['ERROR_INTEGRATION'] if 'ERROR_INTEGRATION' in config else None
    PREDECESSORS = config['PREDECESSORS'] if 'PREDECESSORS' in config and config['PREDECESSORS'] != '' and config['PREDECESSORS'] is not None else []
    OWNER = config['OWNER'] if 'OWNER' in config else None
    COMMENT = config['COMMENT'] if 'COMMENT' in config else None
    ENABLED = config['ENABLED'] if 'ENABLED' in config else None
    CONDITION = config['CONDITION'] if 'CONDITION' in config else None
    USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE = config['USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE'] if 'USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE' in config else None
    USER_TASK_TIMEOUT_MS = str(config['USER_TASK_TIMEOUT_MS']) if 'USER_TASK_TIMEOUT_MS' in config and config['USER_TASK_TIMEOUT_MS'] is not None and str(config['USER_TASK_TIMEOUT_MS']) != '' else None
    SUSPEND_TASK_AFTER_NUM_FAILURES = str(config['SUSPEND_TASK_AFTER_NUM_FAILURES']) if 'SUSPEND_TASK_AFTER_NUM_FAILURES' in config and config['SUSPEND_TASK_AFTER_NUM_FAILURES'] is not None and str(config['SUSPEND_TASK_AFTER_NUM_FAILURES']) != '' else None
    
    TAGS = config['TAGS'] if 'TAGS' in config and config['TAGS'] != '' and config['TAGS'] is not None else []
    BODY = body_code
    GRANTS = config['GRANTS'] if 'GRANTS' in config and config['GRANTS'] != '' and config['GRANTS'] is not None else []
    ENVS = config['DEPLOY_ENV'] if 'DEPLOY_ENV' in config else None

    if WAREHOUSE is not None and WAREHOUSE != '' and USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE is not None and USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE != '':
        raise Exception('Only one of WAREHOUSE or USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE can have a value.')
    #if ((WAREHOUSE is None or WAREHOUSE == '') and (USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE is None or USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE == '')):
    #    raise Exception('WAREHOUSE or USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE must have a value (but only 1).')

    if ENVS is not None and self._deploy_env not in ENVS:
        return_status = 'E'
    else:
        # Check if db exists 

        #task_exists, sf_owner = self._sf.task_check_exists(task_full_name)
        if task_full_name in db_hash_dict:
            task_exists = True
            sf_owner = db_hash_dict[task_full_name]['owner']
            db_hash = db_hash_dict[task_full_name]['db_hash']
        else:
            task_exists = False
            sf_owner = ''
            db_hash = ''
            
        if task_full_name in object_state_dict and object_state_dict[task_full_name]['OBJECT_TYPE'].upper() == 'TASK':
            state_file_hash = object_state_dict[task_full_name]['DEPLOY_HASH']
            state_db_hash = object_state_dict[task_full_name]['DB_HASH']
            state_file_hash_code = object_state_dict[task_full_name]['DEPLOY_HASH_CODE']
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
        if not task_exists:
            # Create database
            self._sf.task_create(task_full_name, WAREHOUSE, SCHEDULE, ALLOW_OVERLAPPING_EXECUTION, ERROR_INTEGRATION, PREDECESSORS, COMMENT, ENABLED, CONDITION, USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE, USER_TASK_TIMEOUT_MS, SUSPEND_TASK_AFTER_NUM_FAILURES, BODY, OWNER, TAGS, GRANTS, self._deploy_role)

            db_hash_new = self._hasher.hash_task(WAREHOUSE, SCHEDULE, ALLOW_OVERLAPPING_EXECUTION, ERROR_INTEGRATION, PREDECESSORS, OWNER, ENABLED, CONDITION, USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE, USER_TASK_TIMEOUT_MS, SUSPEND_TASK_AFTER_NUM_FAILURES, TAGS, BODY, GRANTS)
            self._sf.deploy_hash_apply(task_full_name, 'TASK', file_hash, file_hash_code, db_hash_new, self._deploy_env, self._deploy_db_name)
                
            return_status = 'C'
        else:
            self._handle_ownership(sf_owner, 'task', task_full_name)

            # Get file hash from Snowflake & check if exist
            #sf_deploy_hash = self._sf.deploy_hash_get(self._deploy_db_name, task_full_name, 'task')
            #sf_deploy_code_hash = self._sf.deploy_code_hash_get(self._deploy_db_name, task_full_name, 'task')
            
            if state_file_hash != file_hash or state_file_hash_code != file_hash_code or state_db_hash != db_hash:
                tags_to_remove = list(filter(lambda x: x not in TAGS, db_task[task_full_name]['TAGS_SANS_JINJA']))
                grants_to_remove = list(filter(lambda x: x not in GRANTS, db_task[task_full_name]['GRANTS_SANS_JINJA']))
                
                self._sf.task_alter(task_full_name, WAREHOUSE, SCHEDULE, ALLOW_OVERLAPPING_EXECUTION, ERROR_INTEGRATION, PREDECESSORS, COMMENT, ENABLED, CONDITION, USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE, USER_TASK_TIMEOUT_MS, SUSPEND_TASK_AFTER_NUM_FAILURES, BODY, OWNER, TAGS, GRANTS, self._deploy_role, tags_to_remove, grants_to_remove)
                db_hash_new = self._hasher.hash_task(WAREHOUSE, SCHEDULE, ALLOW_OVERLAPPING_EXECUTION, ERROR_INTEGRATION, PREDECESSORS, OWNER, ENABLED, CONDITION, USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE, USER_TASK_TIMEOUT_MS, SUSPEND_TASK_AFTER_NUM_FAILURES, TAGS, BODY, GRANTS)
                self._sf.deploy_hash_apply(task_full_name, 'TASK', file_hash, file_hash_code, db_hash_new, self._deploy_env, self._deploy_db_name)
                
                return_status = 'U'
            else:
                return_status = 'I'
    return return_status