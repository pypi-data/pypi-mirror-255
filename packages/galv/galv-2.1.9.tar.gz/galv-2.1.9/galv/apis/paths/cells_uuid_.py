from galv.paths.cells_uuid_.get import ApiForget
from galv.paths.cells_uuid_.delete import ApiFordelete
from galv.paths.cells_uuid_.patch import ApiForpatch


class CellsUuid(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
