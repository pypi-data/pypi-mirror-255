import src.common.common as cmn
import json
def hash_masking_policy(self, signiture:list, return_type:str, exempt_other_policies:bool, owner:str, comment:str, tags:list, body:str, grants:list)->str:
    signiture_n = signiture if signiture is not None else []
    return_type_n = return_type if return_type is not None else ''
    exempt_other_policies_n = exempt_other_policies if exempt_other_policies is not None else ''
    owner_n = owner if owner is not None else ''
    comment_n = comment if comment is not None else ''
    tags_n = tags if tags is not None else []
    body_n = body.replace("\n","").strip() if body is not None else ''
    grants_n = grants if grants is not None else []

    signiture_n = cmn.sort_list_of_dicts(signiture_n)
    tags_n = cmn.sort_list_of_dicts(tags_n)
    grants_n = cmn.sort_list_of_dicts(grants_n)

    # NOTE - not including return type as SNOWFLAKE can convert the type in load and vary from the file (ie VARCHAR vs VARCHAR(1453929914) )
    tpl = (signiture_n, exempt_other_policies_n, owner_n, comment_n, tags_n, body_n, grants_n)

    #json_string = json.dumps(tpl)
    #print(json_string)

    hash_value = self.hash(tpl)
    return hash_value
