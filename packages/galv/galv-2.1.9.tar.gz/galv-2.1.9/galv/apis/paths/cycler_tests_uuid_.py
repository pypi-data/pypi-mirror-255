from galv.paths.cycler_tests_uuid_.get import ApiForget
from galv.paths.cycler_tests_uuid_.delete import ApiFordelete
from galv.paths.cycler_tests_uuid_.patch import ApiForpatch


class CyclerTestsUuid(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
