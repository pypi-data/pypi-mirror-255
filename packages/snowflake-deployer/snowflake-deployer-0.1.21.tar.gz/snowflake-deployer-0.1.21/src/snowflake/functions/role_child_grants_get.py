from snowflake.connector import DictCursor
import json

def role_child_grants_get(self,full_role_name:str)->list:
    cur = self._conn.cursor(DictCursor)

    data = []
    try:
        query = "SHOW GRANTS TO ROLE " + full_role_name + ";"
        #cur.execute(query)
        #query = '''
        #    SELECT "name" as CHILD_ROLE, "grant_option" as GRANT_OPTION FROM TABLE(RESULT_SCAN(LAST_QUERY_ID())) WHERE "privilege" = 'USAGE' and "granted_on" = 'ROLE';
        #'''
        cur.execute(query)
        #PARENT_GRANTS = []
        for rec in cur:
            #data.append(rec['CHILD_ROLE'])
            if rec['granted_on'].upper() == 'ROLE':
                data.append(rec['name'])
        #print('######  SQL CHILD GRANTS #######')
        #print('role: '+full_role_name)
        #print(data)
        #print('#############################')
    except Exception as ex:
        msg = 'SQL Error:\n\nQuery: ' + query + '\n\nError Message:\n' + str(ex) + '\n\n'
        raise Exception(msg)
    finally:
        cur.close()
    return data

    