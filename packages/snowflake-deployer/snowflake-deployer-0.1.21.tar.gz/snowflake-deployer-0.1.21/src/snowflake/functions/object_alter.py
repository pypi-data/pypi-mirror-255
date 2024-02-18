def object_alter(self,full_object_name:str, data_retention_time_in_days:int, comment:str, owner:str, change_tracking:bool, row_access_policy:dict, tags:list, grants:list, tags_to_remove:list, grants_to_remove:list):
    cur = self._conn.cursor()
    query = ''
    try:
        # NOTE - alter table will also alter schema
        query = 'ALTER TABLE identifier(%s) SET '
        params = [full_object_name]
        if data_retention_time_in_days is not None:
            query += ' DATA_RETENTION_TIME_IN_DAYS = %s'
            params.append(data_retention_time_in_days)
        if comment is not None:
            query += ' COMMENT = %s'
            params.append(comment)
        if change_tracking is not None:
            query += ' CHANGE_TRACKING = %s'
            params.append(change_tracking)
        if len(params) > 1: # something to execute
            cur.execute(query, params)

        if tags is not None and tags != []:
            for t in tags:
                tag_key = list(t)[0]
                tag_val = t[tag_key]
                query = 'ALTER TABLE identifier(%s) SET TAG identifier(%s) = %s;'
                params = (full_object_name,tag_key,tag_val)
                cur.execute(query,params)

        if owner is not None:
            query = '''
                GRANT OWNERSHIP ON TABLE identifier(%s) TO ROLE identifier(%s) COPY CURRENT GRANTS;
            '''
            cur.execute(query,(full_object_name, owner))

        if row_access_policy is not None and row_access_policy != '' and row_access_policy != {}:

            # Check if row access policy exists on object (can't apply the same row access policy twice)
            row_policy_data = self.object_row_access_policy_reference(full_object_name)
            if row_policy_data == {}:
                query = 'ALTER TABLE identifier(%s) ADD ROW ACCESS POLICY ' + row_access_policy['NAME'] + ' ON ('
                for row_access_policy_column in row_access_policy['INPUT_COLUMNS']:
                    query += '"' + row_access_policy_column + '",'
                query = query[:-1] # remove last comma
                query += ');'
                cur.execute(query,(full_object_name))
            elif row_access_policy['NAME'] != row_policy_data['POLICY_DB'] + '.' + row_policy_data['POLICY_SCHEMA'] + '.' + row_policy_data['POLICY_NAME']:
                old_row_access_policy = row_policy_data['POLICY_DB'] + '.' + row_policy_data['POLICY_SCHEMA'] + '.' + row_policy_data['POLICY_NAME']
                query = '''
                    ALTER TABLE identifier(%s) DROP ROW ACCESS POLICY ''' + old_row_access_policy + ''', ADD ROW ACCESS POLICY ' + row_access_policy['NAME'] + ' ON (
                '''
                for row_access_policy_column in row_access_policy['INPUT_COLUMNS']:
                    query += '"' + row_access_policy_column + '",'
                query = query[:-1] # remove last comma
                query += ');'
                cur.execute(query,(full_object_name))

            # else ignore - row policy on object matches config
            
        if grants is not None:
            for grant in grants:
                grant_keys = grant.keys()
                grant_option = grant['GRANT_OPTION'] if 'GRANT_OPTION' in grant_keys else False
                role = ''
                permission = ''
                for key in grant_keys:
                    if key != 'GRANT_OPTION':
                        role = key
                        permission = grant[key]
                if role != '' and permission != '':
                    query = "GRANT " + permission + " ON TABLE identifier(%s) TO ROLE " + role + ";"
                    cur.execute(query,(full_object_name))
                else:
                    raise Exception('Invalid grants for object: ' + full_object_name)
        
        if tags_to_remove is not None:
            for tag in tags_to_remove:
                #print('%%%')
                #print(tag)
                for tag_name in tag.keys():
                    query = 'ALTER TABLE identifier(%s) UNSET TAG identifier(%s);'
                    params = (full_object_name,tag_name)
                    cur.execute(query,params)

        if grants_to_remove is not None:
            for grant in grants_to_remove:
                for role_name in grant.keys():
                    permission = grant[role_name]
                    query = "REVOKE " + permission + " ON TABLE identifier(%s) FROM ROLE " + role_name + ";"
                    cur.execute(query,(full_object_name))

    except Exception as ex:
        msg = 'SQL Error:\n\nQuery: ' + query + '\n\nError Message:\n' + str(ex) + '\n\n'
        raise Exception(msg)
    finally:
        cur.close()
