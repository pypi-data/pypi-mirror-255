from snowflake.connector import DictCursor

def warehouses_get(self,env_warehouse_prefix:str)->dict:
    cur = self._conn.cursor(DictCursor)
    query = "SHOW WAREHOUSES like '" + env_warehouse_prefix + "%' in ACCOUNT;"
    data=[]
    try:
        cur.execute(query)
        for rec in cur:
            nw = {}
            nw['WAREHOUSE_NAME'] = rec['name'] if rec['name'] is not None else ''
            nw['WAREHOUSE_TYPE'] = rec['type'] if rec['type'] is not None else ''
            nw['WAREHOUSE_SIZE'] = rec['size'] if rec['size'] is not None else ''
            nw['MIN_CLUSTER_COUNT'] = rec['min_cluster_count'] if rec['min_cluster_count'] is not None else ''
            nw['MAX_CLUSTER_COUNT'] = rec['max_cluster_count'] if rec['max_cluster_count'] is not None else ''
            nw['SCALING_POLICY'] = rec['scaling_policy'] if rec['scaling_policy'] is not None else ''
            nw['AUTO_SUSPEND'] = rec['auto_suspend'] if rec['auto_suspend'] is not None else ''
            nw['AUTO_RESUME'] = True if rec['auto_resume'].upper() == 'TRUE' else False
            #nw['RESOURCE_MONITOR'] = rec['resource_monitor']
            nw['OWNER'] = rec['owner'] if rec['owner'] is not None else ''
            nw['COMMENT'] = rec['comment'] if rec['comment'] is not None else ''
            nw['ENABLE_QUERY_ACCELERATION'] = True if rec['enable_query_acceleration'].upper() == 'TRUE' else False
            nw['QUERY_ACCELERATION_MAX_SCALE_FACTOR'] = rec['query_acceleration_max_scale_factor'] if rec['query_acceleration_max_scale_factor'] is not None else ''
            data.append(nw)
    except Exception as ex:
        msg = 'SQL Error:\n\nQuery: ' + query + '\n\nError Message:\n' + str(ex) + '\n\n'
        raise Exception(msg)
    finally:
        cur.close()
    return data