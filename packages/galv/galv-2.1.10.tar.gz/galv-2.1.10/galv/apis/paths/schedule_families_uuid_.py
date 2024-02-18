from galv.paths.schedule_families_uuid_.get import ApiForget
from galv.paths.schedule_families_uuid_.delete import ApiFordelete
from galv.paths.schedule_families_uuid_.patch import ApiForpatch


class ScheduleFamiliesUuid(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
