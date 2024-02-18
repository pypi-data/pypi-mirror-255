from galv.paths.equipment_families_uuid_.get import ApiForget
from galv.paths.equipment_families_uuid_.delete import ApiFordelete
from galv.paths.equipment_families_uuid_.patch import ApiForpatch


class EquipmentFamiliesUuid(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
