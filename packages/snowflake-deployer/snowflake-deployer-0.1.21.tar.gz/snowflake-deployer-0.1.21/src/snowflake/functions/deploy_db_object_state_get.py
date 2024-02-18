from snowflake.connector import DictCursor

def deploy_db_object_state_get(self,deploy_db_name:str, env:str)->dict:
    cur = self._conn.cursor(DictCursor)
    object_full_name = deploy_db_name + '.DEPLOY.OBJECT_STATE'
    query = ''' 
        SELECT OBJECT_TYPE, OBJECT_NAME, DEPLOY_HASH, DB_HASH, DEPLOY_HASH_CODE FROM identifier(%s) WHERE ENV = %s;
    '''

    data={}
    try:
        cur.execute(query,(object_full_name,env))
        for rec in cur:
            nw = {}
            nw['OBJECT_TYPE'] = rec['OBJECT_TYPE']
            nw['DEPLOY_HASH'] = rec['DEPLOY_HASH']
            nw['DB_HASH'] = rec['DB_HASH']       
            nw['DEPLOY_HASH_CODE'] = rec['DEPLOY_HASH_CODE']
            data[rec['OBJECT_NAME']] = nw

    except Exception as ex:
        msg = 'SQL Error:\n\nQuery: ' + query + '\n\nError Message:\n' + str(ex) + '\n\n'
        raise Exception(msg)
    finally:
        cur.close()
    return data




