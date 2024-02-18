from galv.paths.equipment_uuid_.get import ApiForget
from galv.paths.equipment_uuid_.delete import ApiFordelete
from galv.paths.equipment_uuid_.patch import ApiForpatch


class EquipmentUuid(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
