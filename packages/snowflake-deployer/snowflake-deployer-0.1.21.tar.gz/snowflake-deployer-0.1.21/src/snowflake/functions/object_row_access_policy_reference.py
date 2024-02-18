from snowflake.connector import DictCursor
import json

def object_row_access_policy_reference(self,full_object_name:str)->dict:
    # full object name should include any prefixes in the db name
    cur = self._conn.cursor(DictCursor)
    schema_name = full_object_name.split('.')[1]
    database_name = full_object_name.split('.')[0]
    #schema_with_db_name = database_name + '.' + schema_name
    object_name = full_object_name.split('.')[2]
    sql_object_name = '"' + database_name + '"."' + schema_name + '"."' + object_name + '"'
    data=[]
    try:

        #[ "DEPARTMENT" ]
        query = '''
            SELECT POLICY_DB, POLICY_SCHEMA, POLICY_NAME, REF_ARG_COLUMN_NAMES
            FROM table("''' + database_name + '''".INFORMATION_SCHEMA.POLICY_REFERENCES(
                REF_ENTITY_DOMAIN => 'TABLE',
                REF_ENTITY_NAME => %s ))
            WHERE POLICY_KIND = 'ROW_ACCESS_POLICY'
                and POLICY_STATUS = 'ACTIVE'
            ;
        '''
        
        # NOTE there should just be 1 row access policy mapped to a table, so can just use the "last" record in the returned SQL query
        data = {}
        cur.execute(query,(sql_object_name))
        for rec in cur:
            data['POLICY_DB'] = rec['POLICY_DB']
            data['POLICY_SCHEMA'] = rec['POLICY_SCHEMA']
            data['POLICY_NAME'] = rec['POLICY_NAME']
            data['INPUT_COLUMNS_LIST'] = json.loads(rec['REF_ARG_COLUMN_NAMES'].replace("'",'"'))


    except Exception as ex:
        msg = 'SQL Error:\n\nQuery: ' + query + '\n\nError Message:\n' + str(ex) + '\n\n'
        raise Exception(msg)
    finally:
        cur.close()
    return data
