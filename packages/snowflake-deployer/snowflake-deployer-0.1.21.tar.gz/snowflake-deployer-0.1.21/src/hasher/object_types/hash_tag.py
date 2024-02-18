import src.common.common as cmn
#import json
def hash_tag(self, owner:str, comment:str, allowed_values:list, masking_policies:list)->str:
    owner_n = owner if owner is not None else ''
    comment_n = comment if comment is not None else ''
    allowed_values_n = allowed_values if allowed_values is not None else []
    masking_policies_n = masking_policies if masking_policies is not None else []

    allowed_values_n.sort()
    masking_policies_n.sort()

    tpl = (owner_n, comment_n, allowed_values_n, masking_policies_n)
    #print(json.dumps(tpl))
    hash_value = self.hash(tpl)
    return hash_value
