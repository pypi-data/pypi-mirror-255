def hash_task_all(self, dbs:list[dict])->dict:
    data = {}
    for config in dbs:

        WAREHOUSE = config['WAREHOUSE'] if 'WAREHOUSE' in config else None
        SCHEDULE = config['SCHEDULE'] if 'SCHEDULE' in config else None
        ALLOW_OVERLAPPING_EXECUTION = config['ALLOW_OVERLAPPING_EXECUTION'] if 'ALLOW_OVERLAPPING_EXECUTION' in config else None
        ERROR_INTEGRATION = config['ERROR_INTEGRATION'] if 'ERROR_INTEGRATION' in config else None
        PREDECESSORS = config['PREDECESSORS'] if 'PREDECESSORS' in config and config['PREDECESSORS'] != '' and config['PREDECESSORS'] is not None else []
        OWNER = config['OWNER_SANS_JINJA'] if 'OWNER_SANS_JINJA' in config else None
        COMMENT = config['COMMENT'] if 'COMMENT' in config else None
        ENABLED = config['ENABLED'] if 'ENABLED' in config else None
        CONDITION = config['CONDITION'] if 'CONDITION' in config else None
        USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE = config['USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE'] if 'USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE' in config else None
        USER_TASK_TIMEOUT_MS = config['USER_TASK_TIMEOUT_MS'] if 'USER_TASK_TIMEOUT_MS' in config else None
        SUSPEND_TASK_AFTER_NUM_FAILURES = config['SUSPEND_TASK_AFTER_NUM_FAILURES'] if 'SUSPEND_TASK_AFTER_NUM_FAILURES' in config else None
        
        TAGS = config['TAGS_SANS_JINJA'] if 'TAGS_SANS_JINJA' in config and config['TAGS_SANS_JINJA'] != '' and config['TAGS_SANS_JINJA'] is not None else []
        GRANTS = config['GRANTS_SANS_JINJA'] if 'GRANTS_SANS_JINJA' in config and config['GRANTS_SANS_JINJA'] != '' and config['GRANTS_SANS_JINJA'] is not None else []
        BODY = config['DEFINITION'] if 'DEFINITION' in config else None
        
        data[config['FULL_TASK_NAME']] = {}
        data[config['FULL_TASK_NAME']]['owner'] = OWNER
        data[config['FULL_TASK_NAME']]['db_hash'] = self.hash_task(WAREHOUSE, SCHEDULE, ALLOW_OVERLAPPING_EXECUTION, ERROR_INTEGRATION, PREDECESSORS, OWNER, ENABLED, CONDITION, USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE, USER_TASK_TIMEOUT_MS, SUSPEND_TASK_AFTER_NUM_FAILURES, TAGS, BODY, GRANTS)

    return data

    