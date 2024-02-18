def hash_procedure_all(self, dbs:list[dict])->dict:
    data = {}
    for config in dbs:

        INPUT_ARGS = config['INPUT_ARGS'] if 'INPUT_ARGS' in config and config['INPUT_ARGS'] != '' and config['INPUT_ARGS'] is not None else []
        IS_SECURE = config['IS_SECURE'] if 'IS_SECURE' in config else None
        RETURNS = config['RETURNS'] if 'RETURNS' in config else None
        LANGUAGE = config['LANGUAGE'] if 'LANGUAGE' in config else None
        NULL_HANDLING = config['NULL_HANDLING'] if 'NULL_HANDLING' in config else None
        EXECUTE_AS = config['EXECUTE_AS'] if 'EXECUTE_AS' in config else None
        OWNER = config['OWNER_SANS_JINJA'] if 'OWNER_SANS_JINJA' in config else None
        COMMENT = config['COMMENT'] if 'COMMENT' in config else None
        TAGS = config['TAGS_SANS_JINJA'] if 'TAGS_SANS_JINJA' in config and config['TAGS_SANS_JINJA'] != '' and config['TAGS_SANS_JINJA'] is not None else []
        GRANTS = config['GRANTS_SANS_JINJA'] if 'GRANTS_SANS_JINJA' in config and config['GRANTS_SANS_JINJA'] != '' and config['GRANTS_SANS_JINJA'] is not None else []
        BODY = config['BODY'] if 'COMMENT' in config else None
        IMPORTS = config['IMPORTS'] if 'IMPORTS' in config and config['IMPORTS'] != '' and config['IMPORTS'] is not None else []
        HANDLER = config['HANDLER'] if 'HANDLER' in config else None
        RUNTIME_VERSION = config['RUNTIME_VERSION'] if 'RUNTIME_VERSION' in config else None
        PACKAGES = config['PACKAGES'] if 'PACKAGES' in config and config['PACKAGES'] != '' and config['PACKAGES'] is not None else []

        data[config['PROC_FULL_NAME']] = {}
        data[config['PROC_FULL_NAME']]['owner'] = OWNER
        data[config['PROC_FULL_NAME']]['db_hash'] = self.hash_procedure(INPUT_ARGS, IS_SECURE, RETURNS, LANGUAGE, NULL_HANDLING, EXECUTE_AS, OWNER, COMMENT, TAGS, BODY, GRANTS, IMPORTS, HANDLER, RUNTIME_VERSION, PACKAGES)


    return data


    