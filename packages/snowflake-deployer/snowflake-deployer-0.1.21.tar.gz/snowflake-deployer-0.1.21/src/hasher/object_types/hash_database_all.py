def hash_database_all(self, dbs:list[dict])->dict:
    data = {}
    for config in dbs:

        DATA_RETENTION_TIME_IN_DAYS = config['DATA_RETENTION_TIME_IN_DAYS'] if 'DATA_RETENTION_TIME_IN_DAYS' in config else None
        OWNER = config['OWNER_SANS_JINJA'] if 'OWNER_SANS_JINJA' in config else None
        COMMENT = config['COMMENT'] if 'COMMENT' in config else None
        TAGS = config['TAGS_SANS_JINJA'] if 'TAGS_SANS_JINJA' in config else []
        GRANTS = config['GRANTS_SANS_JINJA'] if 'GRANTS_SANS_JINJA' in config and config['GRANTS_SANS_JINJA'] != '' and config['GRANTS_SANS_JINJA'] is not None else []
       
        data[config['DATABASE_NAME']] = {}
        data[config['DATABASE_NAME']]['owner'] = OWNER
        data[config['DATABASE_NAME']]['db_hash'] = self.hash_database(DATA_RETENTION_TIME_IN_DAYS, OWNER, COMMENT, TAGS, GRANTS)

    return data

