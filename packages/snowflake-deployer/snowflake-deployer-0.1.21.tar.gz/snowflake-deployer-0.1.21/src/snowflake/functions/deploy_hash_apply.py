def deploy_hash_apply(self,object_name:str, object_type:str, file_hash:str, file_hash_code:str, db_hash:str, env:str, deploy_db_name:str):     
    cur = self._conn.cursor()
    query = ''
    try:
        object_full_name = deploy_db_name + '.DEPLOY.OBJECT_STATE'
        query = ''' 
            MERGE INTO identifier(%s) t 
            USING
                (SELECT
                    %s as OBJECT_TYPE
                    , %s as OBJECT_NAME
                    , %s as ENV
                    , %s as DEPLOY_HASH
                    , %s as DEPLOY_HASH_CODE
                    , %s as DB_HASH
                    , CURRENT_TIMESTAMP() as LAST_DEPLOY_TIMESTAMP
                ) s
                on t.OBJECT_NAME = s.OBJECT_NAME
                and t.OBJECT_TYPE = s.OBJECT_TYPE
                and t.ENV = s.ENV
            WHEN MATCHED THEN
                UPDATE SET
                    t.DEPLOY_HASH = s.DEPLOY_HASH
                    , t.DEPLOY_HASH_CODE = s.DEPLOY_HASH_CODE
                    ,t.DB_HASH = s.DB_HASH
                    ,t.LAST_DEPLOY_TIMESTAMP = s.LAST_DEPLOY_TIMESTAMP
            WHEN NOT MATCHED THEN
                INSERT (OBJECT_NAME, OBJECT_TYPE, ENV, DEPLOY_HASH, DEPLOY_HASH_CODE, DB_HASH, LAST_DEPLOY_TIMESTAMP)
                VALUES (s.OBJECT_NAME, s.OBJECT_TYPE, s.ENV, s.DEPLOY_HASH, s.DEPLOY_HASH_CODE, s.DB_HASH, s.LAST_DEPLOY_TIMESTAMP)
            ;
        ''' 
        cur.execute(query,(object_full_name, object_type, object_name, env, file_hash, file_hash_code, db_hash))

        #full_tag_name = deploy_db_name + '.TAG.DEPLOY_HASH'
        # NOTE: object_name cannot be an identifier as not all objects will support this
        #query = 'ALTER ' + object_type + ' ' + object_name + ' SET TAG identifier(%s) = %s;'
        #cur.execute(query,(full_tag_name,file_hash))

        #if object_type.upper() == 'TABLE':
        #    # CURRENT_TIMESTAMP is timestamp_ltz
        #    query = 'SET LAST_UPDATE = to_varchar(date_part(epoch_second, current_timestamp()));'
        #    cur.execute(query)
        #    full_tag_name = deploy_db_name + '.TAG.DEPLOY_LAST_UPDATE'
        #    query = 'ALTER ' + object_type + ' ' + object_name + ' SET TAG identifier(%s) = $LAST_UPDATE;'
        #    cur.execute(query,(full_tag_name))
    except Exception as ex:
        msg = 'SQL Error:\n\nQuery: ' + query + '\n\nError Message:\n' + str(ex) + '\n\n'
        raise Exception(msg)
    finally:
        cur.close()
