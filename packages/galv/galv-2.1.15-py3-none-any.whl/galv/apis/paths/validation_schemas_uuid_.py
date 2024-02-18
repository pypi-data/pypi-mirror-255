from galv.paths.validation_schemas_uuid_.get import ApiForget
from galv.paths.validation_schemas_uuid_.put import ApiForput
from galv.paths.validation_schemas_uuid_.delete import ApiFordelete
from galv.paths.validation_schemas_uuid_.patch import ApiForpatch


class ValidationSchemasUuid(
    ApiForget,
    ApiForput,
    ApiFordelete,
    ApiForpatch,
):
    pass
