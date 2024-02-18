from snowflake.connector import DictCursor

def objects_to_classify(self,classify_databases:list, tag_database:str, tag_schema:str)->dict:
    # classify databases must include the actual database names which means they need the prefixes included in them before passing in here
    cur = self._conn.cursor(DictCursor)
    cur_subquery = self._conn.cursor(DictCursor)
    query = ''
    cnt = 1
    #print('######################################')
    #print(classify_databases)
    #print(tag_database)
    #rint('######################################')
    try:
        ############################################################################
        # PART 1 - CHECK FOR TABLES UPDATED WITHIN LAST 4 HOURS
        # 
        # These tables may not be part of SNOWFLAKE.ACCOUNT_USAGE aggregrated
        # metadata and need to be checked individually
        ############################################################################
        
        for db in classify_databases:
            if cnt != 1:
                query += '''
                    UNION ALL
                '''

            query_to_add = '''
                SELECT TABLE_CATALOG as DATABASE_NAME, TABLE_SCHEMA as SCHEMA_NAME, TABLE_NAME as OBJECT_NAME
                    , '"'||TABLE_CATALOG||'"."'||TABLE_SCHEMA||'"."'||TABLE_NAME||'"' as FULL_OBJECT_NAME
                FROM {0}.INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA != 'INFORMATION_SCHEMA' and LAST_DDL >= LOCALTIMESTAMP() - INTERVAL '4 HOURS'
            '''.format(db)
            query += query_to_add 
            cnt += 1
        query += ';'

        cur.execute(query)

        ############################################################################
        # PART 2 - CHECK EACH RECENT TABLE FOR COLUMNS TO CLASSIFY
        # 
        # Ignore columns that already have tags or have a row access policy associated
        ############################################################################
        
        #print('###################  MANUAL ###################')
        tables_checked_manually = []
        objects_to_classify = []
        for rec in cur:
            #print(rec['FULL_OBJECT_NAME'])
            tables_checked_manually.append(rec['FULL_OBJECT_NAME'])
            #rec['DATABASE_NAME']
            #rec['SCHEMA_NAME']
            #rec['OBJECT_NAME']
            
            query = '''
                with data as (
                    SELECT  
                        c.TABLE_CATALOG as DATABASE_NAME, c.TABLE_SCHEMA as SCHEMA_NAME, c.TABLE_NAME as OBJECT_NAME
                        , '"'||c.TABLE_CATALOG||'"."'||c.TABLE_SCHEMA||'"."'||c.TABLE_NAME||'"' as FULL_OBJECT_NAME
                        , case when t.COLUMN_NAME is null and rap.REF_COLUMN_NAME is null then c.COLUMN_NAME end as COLUMN_TO_CLASSIFY
                        , rap.REF_COLUMN_NAME as RAP_COL
                        , t.COLUMN_NAME as TAG_COL
                    FROM {0}.INFORMATION_SCHEMA.COLUMNS c 
                        left join TABLE({1}.INFORMATION_SCHEMA.TAG_REFERENCES_ALL_COLUMNS(%s,'TABLE')) t
                            on c.TABLE_CATALOG = t.OBJECT_DATABASE
                            and c.TABLE_SCHEMA = t.OBJECT_SCHEMA 
                            and c.TABLE_NAME = t.OBJECT_NAME
                            and c.COLUMN_NAME = t.COLUMN_NAME
                            and t.LEVEL = 'COLUMN'
                            and t.TAG_DATABASE = %s
                            and t.TAG_SCHEMA = %s
                            and t.TAG_NAME in ('SENSITIVITY','CLASSIFIED')
                            and t.TAG_VALUE != 'NEW'
                        left join 
                            (WITH base as (
                                SELECT REF_DATABASE_NAME, REF_SCHEMA_NAME, REF_ENTITY_NAME
                                    , parse_json(REF_ARG_COLUMN_NAMES) as REF_ARG_COLUMN_NAMES
                                FROM table({2}.information_schema.policy_references(ref_entity_name => %s, ref_entity_domain => 'table'))
                                WHERE POLICY_KIND = 'ROW_ACCESS_POLICY'
                                )
                                SELECT base.REF_DATABASE_NAME, base.REF_SCHEMA_NAME, base.REF_ENTITY_NAME
                                    , c.VALUE::STRING as REF_COLUMN_NAME
                                FROM base
                                    , LATERAL FLATTEN(base.REF_ARG_COLUMN_NAMES) c
                            ) rap 
                            on c.TABLE_CATALOG = rap.REF_DATABASE_NAME
                            and c.TABLE_SCHEMA = rap.REF_SCHEMA_NAME 
                            and c.TABLE_NAME = rap.REF_ENTITY_NAME
                            and c.COLUMN_NAME = rap.REF_COLUMN_NAME
                    WHERE 
                        c.TABLE_CATALOG = %s
                        and c.TABLE_SCHEMA = %s
                        and c.TABLE_NAME = %s
                    )
                    SELECT FULL_OBJECT_NAME, DATABASE_NAME, SCHEMA_NAME, OBJECT_NAME
                        , sum(case when COLUMN_TO_CLASSIFY is null then 0 else 1 end) as COLUMNS_TO_CLASSIFY_COUNT
                        , listagg(RAP_COL,',') as ROW_ACCESS_COLUMNS
                        , listagg(COLUMN_TO_CLASSIFY,',') as COLUMNS_TO_CLASSIFY
                        , listagg(TAG_COL,',') as TAG_COLUMNS
                    FROM data
                    GROUP BY FULL_OBJECT_NAME, DATABASE_NAME, SCHEMA_NAME, OBJECT_NAME
                    HAVING sum(case when COLUMN_TO_CLASSIFY is null then 0 else 1 end) > 0
                    ;
            '''.format(rec['DATABASE_NAME'],rec['DATABASE_NAME'],tag_database)
            cur_subquery.execute(query,(rec['FULL_OBJECT_NAME'],tag_database, tag_schema, rec['FULL_OBJECT_NAME'],rec['DATABASE_NAME'],rec['SCHEMA_NAME'],rec['OBJECT_NAME']))

            for rec_manual in cur_subquery:
                obj = {}
                obj['FULL_OBJECT_NAME'] = rec_manual['FULL_OBJECT_NAME']
                obj['DATABASE_NAME'] = rec_manual['DATABASE_NAME']
                obj['SCHEMA_NAME'] = rec_manual['SCHEMA_NAME']
                obj['OBJECT_NAME'] = rec_manual['OBJECT_NAME']
                obj['ROW_ACCESS_COLUMNS'] = rec_manual['ROW_ACCESS_COLUMNS']
                obj['COLUMNS_TO_CLASSIFY'] = rec_manual['COLUMNS_TO_CLASSIFY']
                objects_to_classify.append(obj)

        ############################################################################
        # PART 3 - CHECK REMAINDER OF TABLES VIA SNOWFLAKE.ACCOUNT_USAGE
        # 
        # Ignore tables manually checked in PART 2
        ############################################################################
        
        query = '''
            with data as (
            SELECT  
                c.TABLE_CATALOG as DATABASE_NAME, c.TABLE_SCHEMA as SCHEMA_NAME, c.TABLE_NAME as OBJECT_NAME
                , '"'||c.TABLE_CATALOG||'"."'||c.TABLE_SCHEMA||'"."'||c.TABLE_NAME||'"' as FULL_OBJECT_NAME
                , case when t.COLUMN_NAME is null and rap.REF_COLUMN_NAME is null then c.COLUMN_NAME end as COLUMN_TO_CLASSIFY
                , rap.REF_COLUMN_NAME as RAP_COL
                , t.COLUMN_NAME as TAG_COL
            FROM SNOWFLAKE.ACCOUNT_USAGE.COLUMNS c 
                left join SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES t
                    on c.TABLE_CATALOG = t.OBJECT_DATABASE
                    and c.TABLE_SCHEMA = t.OBJECT_SCHEMA 
                    and c.TABLE_NAME = t.OBJECT_NAME
                    and c.COLUMN_NAME = t.COLUMN_NAME
                    and t.DOMAIN = 'COLUMN'
                    and t.TAG_DATABASE = %s
                    and t.TAG_SCHEMA = %s
                    and t.TAG_NAME in ('SENSITIVITY','CLASSIFIED')
                    and t.TAG_VALUE != 'NEW'
                left join 
                    (WITH base as (
                        SELECT REF_DATABASE_NAME, REF_SCHEMA_NAME, REF_ENTITY_NAME
                            , parse_json(REF_ARG_COLUMN_NAMES) as REF_ARG_COLUMN_NAMES
                        FROM SNOWFLAKE.ACCOUNT_USAGE.POLICY_REFERENCES
                        WHERE POLICY_KIND = 'ROW_ACCESS_POLICY'
                        )
                        SELECT base.REF_DATABASE_NAME, base.REF_SCHEMA_NAME, base.REF_ENTITY_NAME
                            , c.VALUE::STRING as REF_COLUMN_NAME
                        FROM base
                            , LATERAL FLATTEN(base.REF_ARG_COLUMN_NAMES) c
                    ) rap 
                    on c.TABLE_CATALOG = rap.REF_DATABASE_NAME
                    and c.TABLE_SCHEMA = rap.REF_SCHEMA_NAME 
                    and c.TABLE_NAME = rap.REF_ENTITY_NAME
                    and c.COLUMN_NAME = rap.REF_COLUMN_NAME
            )
            SELECT FULL_OBJECT_NAME, DATABASE_NAME, SCHEMA_NAME, OBJECT_NAME
                , sum(case when COLUMN_TO_CLASSIFY is null then 0 else 1 end) as COLUMNS_TO_CLASSIFY_COUNT
                , listagg(RAP_COL,',') as ROW_ACCESS_COLUMNS
                , listagg(COLUMN_TO_CLASSIFY,',') as COLUMNS_TO_CLASSIFY
                , listagg(TAG_COL,',') as TAG_COLUMNS
            FROM data
            GROUP BY FULL_OBJECT_NAME, DATABASE_NAME, SCHEMA_NAME, OBJECT_NAME
            HAVING sum(case when COLUMN_TO_CLASSIFY is null then 0 else 1 end) > 0
            ;
        '''
        cur_subquery.execute(query,(tag_database, tag_schema))
        #print('#######  ALL ########')
        for rec_all in cur_subquery:
            if rec_all['FULL_OBJECT_NAME'] not in tables_checked_manually and rec_all['DATABASE_NAME'] in classify_databases:
                #print(rec_all['FULL_OBJECT_NAME'])
                obj = {}
                obj['FULL_OBJECT_NAME'] = rec_all['FULL_OBJECT_NAME']
                obj['DATABASE_NAME'] = rec_all['DATABASE_NAME']
                obj['SCHEMA_NAME'] = rec_all['SCHEMA_NAME']
                obj['OBJECT_NAME'] = rec_all['OBJECT_NAME']
                obj['ROW_ACCESS_COLUMNS'] = rec_all['ROW_ACCESS_COLUMNS']
                obj['COLUMNS_TO_CLASSIFY'] = rec_all['COLUMNS_TO_CLASSIFY']
                objects_to_classify.append(obj)
            
    except Exception as ex:
        msg = 'SQL Error:\n\nQuery: ' + query + '\n\nError Message:\n' + str(ex) + '\n\n'
        raise Exception(msg)
    finally:
        cur.close()
    return objects_to_classify
