def deploy_db_install(self,deploy_db_name: str)->bool:
    cur = self._conn.cursor()
    query = ''
    try:
        # Permissions
        #query = "GRANT CREATE DATABASE ON ACCOUNT TO ROLE INSTANCEADMIN;"
        #cur.execute(query)
        #query = "GRANT CREATE USER ON ACCOUNT TO ROLE INSTANCEADMIN;"
        #cur.execute(query)
        #query = "GRANT CREATE ROLE ON ACCOUNT TO ROLE INSTANCEADMIN;"
        #cur.execute(query)
        #query = "GRANT CREATE WAREHOUSE ON ACCOUNT TO ROLE INSTANCEADMIN;"
        #cur.execute(query)

        query = '''
            CREATE DATABASE IF NOT EXISTS identifier(%s) COMMENT = 'Database to manage deployments using snowflake-deployer'
        '''
        cur.execute(query, (deploy_db_name))

        schema_full_name = deploy_db_name + '.TAG';
        query = '''
            CREATE SCHEMA IF NOT EXISTS identifier(%s) COMMENT = 'Schema to store tags for snowflake-deployer'
        '''
        cur.execute(query, (schema_full_name))

        schema_full_name = deploy_db_name + '.DEPLOY';
        query = '''
            CREATE SCHEMA IF NOT EXISTS identifier(%s) COMMENT = 'Schema to store deployment state for snowflake-deployer'
        '''
        cur.execute(query, (schema_full_name))

        table_full_name = deploy_db_name + '.DEPLOY.OBJECT_STATE';
        query = '''
            CREATE TABLE IF NOT EXISTS identifier(%s) (ENV STRING, OBJECT_TYPE STRING, OBJECT_NAME STRING, DEPLOY_HASH STRING, DEPLOY_HASH_CODE STRING, DB_HASH STRING, LAST_DEPLOY_TIMESTAMP TIMESTAMP_LTZ) COMMENT = 'Schema to store deployment state for snowflake-deployer'
        '''
        cur.execute(query, (table_full_name))

        tag_full_name = deploy_db_name + '.TAG.DEPLOY_HASH';
        query = '''
            CREATE TAG IF NOT EXISTS identifier(%s) COMMENT = 'Tag to store deployment hash for snowflake-deployer'
        '''
        cur.execute(query, (tag_full_name))

        tag_full_name = deploy_db_name + '.TAG.DEPLOY_CODE_HASH';
        query = '''
            CREATE TAG IF NOT EXISTS identifier(%s) COMMENT = 'Tag to store deployment hash for code files for snowflake-deployer'
        '''
        cur.execute(query, (tag_full_name))

        tag_full_name = deploy_db_name + '.TAG.DEPLOY_LAST_UPDATE';
        query = '''
            CREATE TAG IF NOT EXISTS identifier(%s) COMMENT = 'Tag to store last deployment update timestamp for last_ddl comparison for snowflake-deployer'
        '''
        cur.execute(query, (tag_full_name))
        
    except Exception as ex:
        msg = 'SQL Error:\n\nQuery: ' + query + '\n\nError Message:\n' + str(ex) + '\n\n'
        raise Exception(msg)
    finally:
        cur.close()