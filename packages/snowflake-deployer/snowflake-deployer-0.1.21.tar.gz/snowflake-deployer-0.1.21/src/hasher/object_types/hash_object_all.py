def hash_object_all(self, dbs:list[dict])->dict:
    data = {}
    for config in dbs:

        DATA_RETENTION_TIME_IN_DAYS = int(config['DATA_RETENTION_TIME_IN_DAYS']) if 'DATA_RETENTION_TIME_IN_DAYS' in config else None 
        COMMENT = config['COMMENT'] if 'COMMENT' in config else None
        OWNER = config['OWNER_SANS_JINJA'] if 'OWNER_SANS_JINJA' in config else None
        CHANGE_TRACKING = config['CHANGE_TRACKING'] if 'CHANGE_TRACKING' in config else None
        TAGS = config['TAGS_SANS_JINJA'] if 'TAGS_SANS_JINJA' in config and config['TAGS_SANS_JINJA'] != '' and config['TAGS_SANS_JINJA'] is not None else []
        GRANTS = config['GRANTS_SANS_JINJA'] if 'GRANTS_SANS_JINJA' in config and config['GRANTS_SANS_JINJA'] != '' and config['GRANTS_SANS_JINJA'] is not None else []
        COLUMNS = config['COLUMNS'] if 'COLUMNS' in config and config['COLUMNS'] != '' and config['COLUMNS'] is not None else []
        ROW_ACCESS_POLICY = config['ROW_ACCESS_POLICY'] if 'ROW_ACCESS_POLICY' in config else {}
        
        #print('%$%$%$%$%$%$%$%$%$%')
        #print(COLUMNS)
        #print('-------------------')
        NEW_COLS = []
        for c in COLUMNS:
            nc = {}
            nc['NAME'] = c['NAME']
            nc['TAGS'] = c['TAGS_SANS_JINJA'] if 'TAGS_SANS_JINJA' in c and c['TAGS_SANS_JINJA'] != '' and c['TAGS_SANS_JINJA'] is not None else []
            NEW_COLS.append(nc)
        COLUMNS = NEW_COLS
        data[config['FULL_OBJECT_NAME']] = {}
        data[config['FULL_OBJECT_NAME']]['owner'] = OWNER
        data[config['FULL_OBJECT_NAME']]['db_hash'] = self.hash_object(DATA_RETENTION_TIME_IN_DAYS, COMMENT, OWNER, CHANGE_TRACKING, TAGS, COLUMNS, GRANTS, ROW_ACCESS_POLICY)

    return data

