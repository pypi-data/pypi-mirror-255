from galv.paths.cell_families_uuid_.get import ApiForget
from galv.paths.cell_families_uuid_.delete import ApiFordelete
from galv.paths.cell_families_uuid_.patch import ApiForpatch


class CellFamiliesUuid(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
