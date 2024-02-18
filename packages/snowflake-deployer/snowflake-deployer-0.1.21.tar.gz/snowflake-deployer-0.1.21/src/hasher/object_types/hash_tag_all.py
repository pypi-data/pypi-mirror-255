def hash_tag_all(self, rs:list[dict])->dict:
    data = {}
    for config in rs:

        OWNER = config['OWNER_SANS_JINJA'] if 'OWNER_SANS_JINJA' in config else None
        COMMENT = config['COMMENT'] if 'COMMENT' in config else None
        ALLOWED_VALUES = config['ALLOWED_VALUES'] if 'ALLOWED_VALUES' in config and config['ALLOWED_VALUES'] != '' and config['ALLOWED_VALUES'] is not None else []
        MASKING_POLICIES = config['MASKING_POLICIES_SANS_JINJA'] if 'MASKING_POLICIES_SANS_JINJA' in config and config['MASKING_POLICIES_SANS_JINJA'] != '' and config['MASKING_POLICIES_SANS_JINJA'] is not None else []
       
        data[config['FULL_TAG_NAME']] = {}
        data[config['FULL_TAG_NAME']]['owner'] = OWNER
        data[config['FULL_TAG_NAME']]['db_hash'] = self.hash_tag(OWNER, COMMENT, ALLOWED_VALUES, MASKING_POLICIES)

    return data
