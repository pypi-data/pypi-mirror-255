def hash_role_all(self, rs:list[dict])->dict:
    data = {}
    for config in rs:

        OWNER = config['OWNER_SANS_JINJA'] if 'OWNER_SANS_JINJA' in config else None
        COMMENT = config['COMMENT'] if 'COMMENT' in config else None
        CHILD_ROLES = config['CHILD_ROLES_SANS_JINJA'] if 'CHILD_ROLES_SANS_JINJA' in config else []
        TAGS = config['TAGS_SANS_JINJA'] if 'TAGS_SANS_JINJA' in config and config['TAGS_SANS_JINJA'] != '' and config['TAGS_SANS_JINJA'] is not None else []
       
        data[config['ROLE_NAME']] = {}
        data[config['ROLE_NAME']]['owner'] = OWNER
        #print(config['ROLE_NAME'])
        data[config['ROLE_NAME']]['db_hash'] = self.hash_role(OWNER, COMMENT, CHILD_ROLES, TAGS)

    return data
