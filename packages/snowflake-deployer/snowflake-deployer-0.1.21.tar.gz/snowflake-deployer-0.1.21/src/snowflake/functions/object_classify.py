from snowflake.connector import DictCursor

def object_classify(self,full_table_name:str,max_sample_size:int)->dict:
    cur = self._conn.cursor(DictCursor)
    max_sample_size_str = str(max_sample_size)
    query = '''
        WITH data as (
            SELECT
                f.key::varchar as COLUMN_NAME
                , f.value:"recommendation":"privacy_category"::varchar as PRIVACY_CATEGORY
                , f.value:"recommendation":"semantic_category"::varchar as SEMANTIC_CATEGORY
                , f.value:"recommendation":"coverage"::number(10,2) as PROBABILITY
                , f.value:"recommendation":"alternates"::variant as ALTERNATES
            FROM
                TABLE(FLATTEN(EXTRACT_SEMANTIC_CATEGORIES(%s,''' + max_sample_size_str + ''')::VARIANT)) AS f
        )
        , flattened_alternatives as (
            SELECT
                d.COLUMN_NAME
                , coalesce(d.PRIVACY_CATEGORY, a.value:"privacy_category"::STRING,'') as PRIVACY_CATEGORY
                , coalesce(d.SEMANTIC_CATEGORY, a.value:"semantic_category"::STRING,'') as SEMANTIC_CATEGORY
                , coalesce(d.PROBABILITY, a.value:"probability"::NUMBER(38,2),0)::STRING as PROBABILITY
                --, d.ALTERNATIVES
                --, a.value:"privacy_category"::STRING as ALT_PRIVACY_CATEGORY
                --, a.value:"probability"::NUMBER(38,2) as ALT_PROBABILITY
                --, a.value:"semantic_category"::STRING as ALT_SEMANTIC_CATEGORY
            FROM data d
                , TABLE(FLATTEN(d.ALTERNATES, OUTER=> TRUE)) a
            QUALIFY row_number() over (PARTITION BY d.COLUMN_NAME ORDER BY a.value:"probability"::NUMBER(38,2) DESC) = 1 -- get top alternative
        )
        SELECT
            COLUMN_NAME
            , PRIVACY_CATEGORY
            , SEMANTIC_CATEGORY
            , PROBABILITY
            , case
                when PRIVACY_CATEGORY in ('IDENTIFIER', 'QUASI_IDENTIFIER') then 'CONFIDENTIAL'
                when PRIVACY_CATEGORY in ('SENSITIVE') then 'RESTRICTED'
                when PRIVACY_CATEGORY is null or PRIVACY_CATEGORY = '' then 'INTERNAL'
                else PRIVACY_CATEGORY
            end TAG_SENSITIVITY
        FROM flattened_alternatives
        ;
    '''
    data=[]
    try:
        cur.execute(query,(full_table_name))
        for rec in cur:
            nw = {}
            nw['FULL_TABLE_NAME'] = full_table_name
            nw['COLUMN_NAME'] = rec['COLUMN_NAME']
            nw['PRIVACY_CATEGORY'] = rec['PRIVACY_CATEGORY']
            nw['SEMANTIC_CATEGORY'] = rec['SEMANTIC_CATEGORY']
            nw['PROBABILITY'] = rec['PROBABILITY']
            nw['TAG_SENSITIVITY'] = rec['TAG_SENSITIVITY']
            data.append(nw)
    except Exception as ex:
        msg = 'SQL Error:\n\nQuery: ' + query + '\n\nError Message:\n' + str(ex) + '\n\n'
        raise Exception(msg)
    finally:
        cur.close()
    return data
