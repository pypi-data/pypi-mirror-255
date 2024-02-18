def hash_schema_all(self, ss:list[dict])->dict:
    data = {}
    for config in ss:

        DATA_RETENTION_TIME_IN_DAYS = config['DATA_RETENTION_TIME_IN_DAYS'] if 'DATA_RETENTION_TIME_IN_DAYS' in config else None
        OWNER = config['OWNER_SANS_JINJA'] if 'OWNER_SANS_JINJA' in config else None
        COMMENT = config['COMMENT'] if 'COMMENT' in config else None
        TAGS = config['TAGS_SANS_JINJA'] if 'TAGS_SANS_JINJA' in config else []
        GRANTS = config['GRANTS_SANS_JINJA'] if 'GRANTS_SANS_JINJA' in config and config['GRANTS_SANS_JINJA'] != '' and config['GRANTS_SANS_JINJA'] is not None else []
       
        data[config['FULL_SCHEMA_NAME']] = {}
        data[config['FULL_SCHEMA_NAME']]['owner'] = OWNER
        data[config['FULL_SCHEMA_NAME']]['db_hash'] = self.hash_schema(DATA_RETENTION_TIME_IN_DAYS, OWNER, COMMENT, TAGS, GRANTS)

    return data
