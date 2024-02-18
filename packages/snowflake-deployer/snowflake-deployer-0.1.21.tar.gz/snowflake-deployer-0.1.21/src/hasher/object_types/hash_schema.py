import src.common.common as cmn
def hash_schema(self, data_retention_time_in_days:int, owner:str, comment:str, tags:list, grants:list)->str:
    data_retention_time_in_days_n = data_retention_time_in_days if data_retention_time_in_days is not None else ''
    owner_n = owner if owner is not None else ''
    comment_n = comment if comment is not None else ''
    tags_n = tags if tags is not None else []
    grants_n = grants if grants is not None else []

    tags_n = cmn.sort_list_of_dicts(tags_n)
    grants_n = cmn.sort_list_of_dicts(grants_n)

    tpl = (data_retention_time_in_days_n, owner_n, comment_n, tags_n, grants_n)
    hash_value = self.hash(tpl)
    return hash_value
