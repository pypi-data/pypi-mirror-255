import json
import src.common.common as cmn
def hash_role(self, owner:str, comment:str, child_roles:list, tags:list)->str:
    owner_n = owner if owner is not None else ''
    comment_n = comment if comment is not None else ''
    child_roles_n = child_roles if child_roles is not None else []
    tags_n = tags if tags is not None else []

    child_roles_n.sort()
    tags_n = cmn.sort_list_of_dicts(tags_n)

    tpl = (owner_n, comment_n, child_roles_n, tags_n)
    #print(json.dumps(tpl))
    hash_value = self.hash(tpl)
    return hash_value
