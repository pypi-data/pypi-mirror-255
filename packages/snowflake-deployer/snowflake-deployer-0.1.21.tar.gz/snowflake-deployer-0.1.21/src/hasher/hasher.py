from hashlib import sha256
import json 

class hasher:
    def __init__(self):
    #    #self._sf = sf
        self._test = 'test'

    def hash(self, tpl:tuple)->str:
        json_string = json.dumps(tpl)
        #print('***** JSON TEST *****')
        #print(json_string)
        sha = sha256()
        sha.update(str(json_string).encode('utf-8'))
        hash_val = sha.hexdigest()
        #print(hash_val)
        #print('***** END JSON TEST *****')
        return hash_val

    from .object_types.hash_database_all import hash_database_all
    from .object_types.hash_database import hash_database
    from .object_types.hash_function_all import hash_function_all
    from .object_types.hash_function import hash_function
    from .object_types.hash_masking_policy_all import hash_masking_policy_all
    from .object_types.hash_masking_policy import hash_masking_policy
    from .object_types.hash_object_all import hash_object_all
    from .object_types.hash_object import hash_object
    from .object_types.hash_procedure_all import hash_procedure_all
    from .object_types.hash_procedure import hash_procedure
    from .object_types.hash_role_all import hash_role_all
    from .object_types.hash_role import hash_role
    from .object_types.hash_row_access_policy_all import hash_row_access_policy_all
    from .object_types.hash_row_access_policy import hash_row_access_policy
    from .object_types.hash_schema_all import hash_schema_all
    from .object_types.hash_schema import hash_schema
    from .object_types.hash_tag_all import hash_tag_all
    from .object_types.hash_tag import hash_tag
    from .object_types.hash_task_all import hash_task_all
    from .object_types.hash_task import hash_task
    from .object_types.hash_warehouse_all import hash_warehouse_all
    from .object_types.hash_warehouse import hash_warehouse