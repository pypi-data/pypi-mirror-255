import src.common.common as cmn
def hash_warehouse(self, warehouse_type:str, warehouse_size:str, min_cluster_count:int, max_cluster_count:int, scaling_policy:str, auto_suspend:int, auto_resume:bool, owner:str, comment:str, enable_query_acceleration:bool, query_acceleration_max_scale_factor:int, tags:list, grants:list)->str:
    warehouse_type_n = warehouse_type if warehouse_type is not None else ''
    warehouse_size_n = warehouse_size if warehouse_size is not None else ''
    min_cluster_count_n = min_cluster_count if min_cluster_count is not None else ''
    max_cluster_count_n = max_cluster_count if max_cluster_count is not None else ''
    scaling_policy_n = scaling_policy if scaling_policy is not None else ''
    auto_suspend_n = auto_suspend if auto_suspend is not None else ''
    auto_resume_n = auto_resume if auto_resume is not None else ''
    owner_n = owner if owner is not None else ''
    comment_n = comment if comment is not None else ''
    enable_query_acceleration_n = enable_query_acceleration if enable_query_acceleration is not None else ''
    query_acceleration_max_scale_factor_n = query_acceleration_max_scale_factor if query_acceleration_max_scale_factor is not None else ''
    tags_n = tags if tags is not None else []
    grants_n = grants if grants is not None else []
    
    tags_n = cmn.sort_list_of_dicts(tags_n)
    grants_n = cmn.sort_list_of_dicts(grants_n)

    tpl = (warehouse_type_n, warehouse_size_n, min_cluster_count_n, max_cluster_count_n, scaling_policy_n, auto_suspend_n, auto_resume_n, owner_n, comment_n, enable_query_acceleration_n, query_acceleration_max_scale_factor_n, tags_n, grants_n)
    hash_value = self.hash(tpl)
    return hash_value