from deci_platform_client.paths.workspaces_id.get import ApiForget
from deci_platform_client.paths.workspaces_id.delete import ApiFordelete
from deci_platform_client.paths.workspaces_id.patch import ApiForpatch


class WorkspacesId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
