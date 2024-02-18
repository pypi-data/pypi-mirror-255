def role_alter(self,role_name, owner:str, comment:str, child_roles:list, tags:list, tags_to_remove:list, grants_to_remove:list):
    cur = self._conn.cursor()
    query = ''
    try:
        query = 'ALTER ROLE identifier(%s) SET '
        params = [role_name]
        if comment is not None:
            query += ' COMMENT = %s'
            params.append(comment)
        if len(params) > 1: # something to execute
            cur.execute(query, params)

        if tags is not None and tags != []:
            for t in tags:
                tag_key = list(t)[0]
                tag_val = t[tag_key]
                query = 'ALTER ROLE identifier(%s) SET TAG identifier(%s) = %s;'
                params = (role_name,tag_key,tag_val)
                cur.execute(query,params)

        if child_roles is not None and child_roles != []:
            for child_role in child_roles:
                query = "GRANT ROLE " + child_role + " TO ROLE " + role_name + ";"
                cur.execute(query)
                
        if owner is not None:
            query = '''
                GRANT OWNERSHIP ON ROLE identifier(%s) TO ROLE identifier(%s) COPY CURRENT GRANTS;
            '''
            cur.execute(query,(role_name, owner))
        
        if tags_to_remove is not None:
            for tag in tags_to_remove:
                for tag_name in tag.keys():
                    query = 'ALTER ROLE identifier(%s) UNSET TAG identifier(%s);'
                    params = (role_name,tag_name)
                    cur.execute(query,params)

        if grants_to_remove is not None:
            for grant in grants_to_remove:
                for child_role in grant.keys():
                    #permission = grant[child_role]
                    query = "REVOKE role " + child_role + " FROM ROLE " + role_name + ";"
                    cur.execute(query)

    except Exception as ex:
        msg = 'SQL Error:\n\nQuery: ' + query + '\n\nError Message:\n' + str(ex) + '\n\n'
        raise Exception(msg)
    finally:
        cur.close()
