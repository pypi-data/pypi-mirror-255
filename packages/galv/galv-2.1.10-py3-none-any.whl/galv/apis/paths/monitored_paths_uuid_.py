from galv.paths.monitored_paths_uuid_.get import ApiForget
from galv.paths.monitored_paths_uuid_.delete import ApiFordelete
from galv.paths.monitored_paths_uuid_.patch import ApiForpatch


class MonitoredPathsUuid(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
