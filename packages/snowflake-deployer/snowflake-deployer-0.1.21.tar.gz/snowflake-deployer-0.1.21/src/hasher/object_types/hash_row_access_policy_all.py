def hash_row_access_policy_all(self, dbs:list[dict])->dict:
    data = {}
    for config in dbs:

        SIGNATURE = config['SIGNATURE'] if 'SIGNATURE' in config and config['SIGNATURE'] != '' and config['SIGNATURE'] is not None else []
        RETURN_TYPE = config['RETURN_TYPE'] if 'RETURN_TYPE' in config else None
        OWNER = config['OWNER_SANS_JINJA'] if 'OWNER_SANS_JINJA' in config else None
        COMMENT = config['COMMENT'] if 'COMMENT' in config else None

        TAGS = config['TAGS_SANS_JINJA'] if 'TAGS_SANS_JINJA' in config and config['TAGS_SANS_JINJA'] != '' and config['TAGS_SANS_JINJA'] is not None else []
        GRANTS = config['GRANTS_SANS_JINJA'] if 'GRANTS_SANS_JINJA' in config and config['GRANTS_SANS_JINJA'] != '' and config['GRANTS_SANS_JINJA'] is not None else []
        BODY = config['BODY'] if 'BODY' in config else None
        
        data[config['FULL_POLICY_NAME']] = {}
        data[config['FULL_POLICY_NAME']]['owner'] = OWNER
        data[config['FULL_POLICY_NAME']]['db_hash'] = self.hash_row_access_policy(SIGNATURE, RETURN_TYPE, OWNER, COMMENT, TAGS, BODY, GRANTS)

    return data


    
