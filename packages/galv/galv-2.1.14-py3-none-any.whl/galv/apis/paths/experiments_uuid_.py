from galv.paths.experiments_uuid_.get import ApiForget
from galv.paths.experiments_uuid_.delete import ApiFordelete
from galv.paths.experiments_uuid_.patch import ApiForpatch


class ExperimentsUuid(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
