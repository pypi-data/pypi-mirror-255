import src.common.common as cmn
import json
def hash_task(self, warehouse:str, schedule:str, allow_overlapping_execution:bool, error_integration:str, predecessors:list, owner:str, enabled:bool, condition:str, user_task_managed_initial_warehouse_size:str, user_task_timeout_ms:str, suspend_task_after_num_failures:str, tags:list, body:str, grants:list)->str:
    warehouse_n = warehouse if warehouse is not None else ''
    schedule_n = schedule if schedule is not None else ''
    allow_overlapping_execution_n = allow_overlapping_execution if allow_overlapping_execution is not None else ''
    error_integration_n = error_integration if error_integration is not None else ''
    predecessors_n = predecessors if predecessors is not None else []
    owner_n = owner if owner is not None else ''
    enabled_n = enabled if enabled is not None else ''
    condition_n = condition if condition is not None else ''
    user_task_managed_initial_warehouse_size_n = user_task_managed_initial_warehouse_size if user_task_managed_initial_warehouse_size is not None else ''
    user_task_timeout_ms_n = user_task_timeout_ms if user_task_timeout_ms is not None else ''
    suspend_task_after_num_failures_n = suspend_task_after_num_failures if suspend_task_after_num_failures is not None else ''
    
    tags_n = tags if tags is not None else []
    body_n = body.replace("\n","").strip() if body is not None else ''
    grants_n = grants if grants is not None else []

    predecessors_n.sort()
    tags_n = cmn.sort_list_of_dicts(tags_n)
    grants_n = cmn.sort_list_of_dicts(grants_n)

    # NOTE - the following cannot be queried in Snowflake, and should not be part of the hash (else it will always trigger an update)
    #USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE
    #USER_TASK_TIMEOUT_MS
    #SUSPEND_TASK_AFTER_NUM_FAILURES
    tpl = (warehouse_n, schedule_n, allow_overlapping_execution_n, error_integration_n, predecessors_n, owner_n, enabled_n, condition_n, tags_n, body_n, grants_n)
    #json_string = json.dumps(tpl)
    #print(json_string)

    hash_value = self.hash(tpl)
    return hash_value


