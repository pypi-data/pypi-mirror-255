import src.common.common as cmn
import json
def hash_function(self, input_args:list, is_secure:bool, returns:str, language:str, owner:str, comment:str, tags:list, body:str, grants:list, imports:list, handler:str, runtime_version:str, packages:list)->str:
    input_args_n = input_args if input_args is not None else []
    is_secure_n = is_secure if is_secure is not None else ''
    returns_n = returns if returns is not None else ''
    language_n = language if language is not None else ''
    owner_n = owner if owner is not None else ''
    comment_n = comment if comment is not None else ''
    tags_n = tags if tags is not None else []
    body_n = body.replace("\n","").strip() if body is not None else ''
    grants_n = grants if grants is not None else []
    imports_n = imports if imports is not None else []
    handler_n = handler if handler is not None else ''
    runtime_version_n = str(runtime_version) if runtime_version is not None else ''
    packages_n = packages if packages is not None else []
    
    input_args_n = cmn.sort_list_of_dicts(input_args_n)
    tags_n = cmn.sort_list_of_dicts(tags_n)
    grants_n = cmn.sort_list_of_dicts(grants_n)
    imports_n.sort()
    packages_n.sort()

    # NOTE - not including return type as SNOWFLAKE can convert the type in load and vary from the file (ie VARCHAR vs VARCHAR(1453929914) )
    
    tpl = (input_args_n, is_secure_n, language_n, owner_n, comment_n, tags_n, body_n, grants_n, imports_n, handler_n, runtime_version_n,  packages_n)
    
    #json_string = json.dumps(tpl)
    #print(json_string)

    hash_value = self.hash(tpl)
    return hash_value
