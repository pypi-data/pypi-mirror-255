import src.common.common as cmn
import json
def hash_row_access_policy(self, signature:list, return_type:str, owner:str, comment:str, tags:list, body:str, grants:list)->str:
    signature_n = signature if signature is not None else []
    return_type_n = return_type if return_type is not None else ''
    comment_n = comment if comment is not None else ''
    tags_n = tags if tags is not None else []
    body_n = body.replace("\n","").strip() if tags is not None else ''
    grants_n = grants if grants is not None else []

    signature_n = cmn.sort_list_of_dicts(signature_n)
    tags_n = cmn.sort_list_of_dicts(tags_n)
    grants_n = cmn.sort_list_of_dicts(grants_n)

    # NOTE - not including return type as SNOWFLAKE can convert the type in load and vary from the file (ie VARCHAR vs VARCHAR(1453929914) )
    
    tpl = (signature_n, comment_n, tags_n, body_n, grants_n)

    #json_string = json.dumps(tpl)
    #print(json_string)

    hash_value = self.hash(tpl)
    return hash_value



