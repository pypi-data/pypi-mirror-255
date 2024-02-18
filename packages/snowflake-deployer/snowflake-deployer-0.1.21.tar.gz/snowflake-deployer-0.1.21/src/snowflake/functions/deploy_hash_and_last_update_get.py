#from snowflake.connector import DictCursor

def deploy_hash_and_last_update_get(self,deploy_db_name:str, object:str, object_type:str)->str:
    cur = self._conn.cursor()
    full_tag_name = deploy_db_name + '.TAG.DEPLOY_HASH'
    full_tag_name_last_update = deploy_db_name + '.TAG.DEPLOY_LAST_UPDATE'


    query = '''
        SELECT system$get_tag(%s, %s, %s) as TAG_VALUE, COALESCE(system$get_tag(%s, %s, %s),date_part(epoch_second,cast('1900-01-01' as timestamp_ltz))) as LAST_UPDATE; 
    '''
   
    data=[]
    try:
        res = cur.execute(query,(full_tag_name, object, object_type, full_tag_name_last_update, object, object_type)).fetchall()
        tag_value = res[0][0]
        last_update = res[0][1]
    except Exception as ex:
        msg = 'SQL Error:\n\nQuery: ' + query + '\n\nError Message:\n' + str(ex) + '\n\n'
        raise Exception(msg)
    finally:
        cur.close()
    return tag_value, last_update
