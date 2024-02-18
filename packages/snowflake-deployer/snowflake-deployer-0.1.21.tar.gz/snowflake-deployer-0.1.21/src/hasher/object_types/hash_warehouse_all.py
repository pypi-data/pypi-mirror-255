def hash_warehouse_all(self, whs:list[dict])->dict:
    data = {}
    for config in whs:

        WAREHOUSE_TYPE = config['WAREHOUSE_TYPE'] if 'WAREHOUSE_TYPE' in config else None
        WAREHOUSE_SIZE = config['WAREHOUSE_SIZE'] if 'WAREHOUSE_SIZE' in config else None
        MIN_CLUSTER_COUNT = config['MIN_CLUSTER_COUNT'] if 'MIN_CLUSTER_COUNT' in config else None
        MAX_CLUSTER_COUNT = config['MAX_CLUSTER_COUNT'] if 'MAX_CLUSTER_COUNT' in config else None
        SCALING_POLICY = config['SCALING_POLICY'] if 'SCALING_POLICY' in config else None
        AUTO_SUSPEND = config['AUTO_SUSPEND'] if 'AUTO_SUSPEND' in config else None
        AUTO_RESUME = config['AUTO_RESUME'] if 'AUTO_RESUME' in config else None
        OWNER = config['OWNER_SANS_JINJA'] if 'OWNER_SANS_JINJA' in config else None
        COMMENT = config['COMMENT'] if 'COMMENT' in config else None
        ENABLE_QUERY_ACCELERATION = config['ENABLE_QUERY_ACCELERATION'] if 'ENABLE_QUERY_ACCELERATION' in config else None
        QUERY_ACCELERATION_MAX_SCALE_FACTOR = config['QUERY_ACCELERATION_MAX_SCALE_FACTOR'] if 'QUERY_ACCELERATION_MAX_SCALE_FACTOR' in config else None
        TAGS = config['TAGS_SANS_JINJA'] if 'TAGS_SANS_JINJA' in config and config['TAGS_SANS_JINJA'] != '' and config['TAGS_SANS_JINJA'] is not None else []
        GRANTS = config['GRANTS_SANS_JINJA'] if 'GRANTS_SANS_JINJA' in config and config['GRANTS_SANS_JINJA'] != '' and config['GRANTS_SANS_JINJA'] is not None else []
        
        data[config['WAREHOUSE_NAME']] = {}
        data[config['WAREHOUSE_NAME']]['owner'] = OWNER
        data[config['WAREHOUSE_NAME']]['db_hash'] = self.hash_warehouse(WAREHOUSE_TYPE, WAREHOUSE_SIZE, MIN_CLUSTER_COUNT, MAX_CLUSTER_COUNT, SCALING_POLICY, AUTO_SUSPEND, AUTO_RESUME, OWNER, COMMENT, ENABLE_QUERY_ACCELERATION, QUERY_ACCELERATION_MAX_SCALE_FACTOR, TAGS, GRANTS)

    return data
 