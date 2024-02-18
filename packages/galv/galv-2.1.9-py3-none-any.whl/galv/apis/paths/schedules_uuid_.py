from galv.paths.schedules_uuid_.get import ApiForget
from galv.paths.schedules_uuid_.delete import ApiFordelete
from galv.paths.schedules_uuid_.patch import ApiForpatch


class SchedulesUuid(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
