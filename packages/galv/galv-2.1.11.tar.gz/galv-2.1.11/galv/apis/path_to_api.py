import typing_extensions

from galv.paths import PathValues
from galv.apis.paths.access_levels_ import AccessLevels
from galv.apis.paths.activate_ import Activate
from galv.apis.paths.cell_chemistries_ import CellChemistries
from galv.apis.paths.cell_families_ import CellFamilies
from galv.apis.paths.cell_families_uuid_ import CellFamiliesUuid
from galv.apis.paths.cell_form_factors_ import CellFormFactors
from galv.apis.paths.cell_manufacturers_ import CellManufacturers
from galv.apis.paths.cell_models_ import CellModels
from galv.apis.paths.cells_ import Cells
from galv.apis.paths.cells_uuid_ import CellsUuid
from galv.apis.paths.cells_uuid_rdf_ import CellsUuidRdf
from galv.apis.paths.column_types_ import ColumnTypes
from galv.apis.paths.column_types_id_ import ColumnTypesId
from galv.apis.paths.columns_ import Columns
from galv.apis.paths.columns_id_ import ColumnsId
from galv.apis.paths.columns_id_values_ import ColumnsIdValues
from galv.apis.paths.create_token_ import CreateToken
from galv.apis.paths.cycler_tests_ import CyclerTests
from galv.apis.paths.cycler_tests_uuid_ import CyclerTestsUuid
from galv.apis.paths.equipment_ import Equipment
from galv.apis.paths.equipment_uuid_ import EquipmentUuid
from galv.apis.paths.equipment_families_ import EquipmentFamilies
from galv.apis.paths.equipment_families_uuid_ import EquipmentFamiliesUuid
from galv.apis.paths.equipment_manufacturers_ import EquipmentManufacturers
from galv.apis.paths.equipment_models_ import EquipmentModels
from galv.apis.paths.equipment_types_ import EquipmentTypes
from galv.apis.paths.experiments_ import Experiments
from galv.apis.paths.experiments_uuid_ import ExperimentsUuid
from galv.apis.paths.files_ import Files
from galv.apis.paths.files_uuid_ import FilesUuid
from galv.apis.paths.files_uuid_reimport_ import FilesUuidReimport
from galv.apis.paths.harvest_errors_ import HarvestErrors
from galv.apis.paths.harvest_errors_id_ import HarvestErrorsId
from galv.apis.paths.harvesters_ import Harvesters
from galv.apis.paths.harvesters_uuid_ import HarvestersUuid
from galv.apis.paths.labs_ import Labs
from galv.apis.paths.labs_id_ import LabsId
from galv.apis.paths.login_ import Login
from galv.apis.paths.monitored_paths_ import MonitoredPaths
from galv.apis.paths.monitored_paths_uuid_ import MonitoredPathsUuid
from galv.apis.paths.schedule_families_ import ScheduleFamilies
from galv.apis.paths.schedule_families_uuid_ import ScheduleFamiliesUuid
from galv.apis.paths.schedule_identifiers_ import ScheduleIdentifiers
from galv.apis.paths.schedules_ import Schedules
from galv.apis.paths.schedules_uuid_ import SchedulesUuid
from galv.apis.paths.schema_validations_ import SchemaValidations
from galv.apis.paths.schema_validations_id_ import SchemaValidationsId
from galv.apis.paths.teams_ import Teams
from galv.apis.paths.teams_id_ import TeamsId
from galv.apis.paths.tokens_ import Tokens
from galv.apis.paths.tokens_id_ import TokensId
from galv.apis.paths.units_ import Units
from galv.apis.paths.units_id_ import UnitsId
from galv.apis.paths.users_ import Users
from galv.apis.paths.users_id_ import UsersId
from galv.apis.paths.validation_schemas_ import ValidationSchemas
from galv.apis.paths.validation_schemas_uuid_ import ValidationSchemasUuid
from galv.apis.paths.validation_schemas_keys_ import ValidationSchemasKeys

PathToApi = typing_extensions.TypedDict(
    'PathToApi',
    {
        PathValues.ACCESS_LEVELS_: AccessLevels,
        PathValues.ACTIVATE_: Activate,
        PathValues.CELL_CHEMISTRIES_: CellChemistries,
        PathValues.CELL_FAMILIES_: CellFamilies,
        PathValues.CELL_FAMILIES_UUID_: CellFamiliesUuid,
        PathValues.CELL_FORM_FACTORS_: CellFormFactors,
        PathValues.CELL_MANUFACTURERS_: CellManufacturers,
        PathValues.CELL_MODELS_: CellModels,
        PathValues.CELLS_: Cells,
        PathValues.CELLS_UUID_: CellsUuid,
        PathValues.CELLS_UUID_RDF_: CellsUuidRdf,
        PathValues.COLUMN_TYPES_: ColumnTypes,
        PathValues.COLUMN_TYPES_ID_: ColumnTypesId,
        PathValues.COLUMNS_: Columns,
        PathValues.COLUMNS_ID_: ColumnsId,
        PathValues.COLUMNS_ID_VALUES_: ColumnsIdValues,
        PathValues.CREATE_TOKEN_: CreateToken,
        PathValues.CYCLER_TESTS_: CyclerTests,
        PathValues.CYCLER_TESTS_UUID_: CyclerTestsUuid,
        PathValues.EQUIPMENT_: Equipment,
        PathValues.EQUIPMENT_UUID_: EquipmentUuid,
        PathValues.EQUIPMENT_FAMILIES_: EquipmentFamilies,
        PathValues.EQUIPMENT_FAMILIES_UUID_: EquipmentFamiliesUuid,
        PathValues.EQUIPMENT_MANUFACTURERS_: EquipmentManufacturers,
        PathValues.EQUIPMENT_MODELS_: EquipmentModels,
        PathValues.EQUIPMENT_TYPES_: EquipmentTypes,
        PathValues.EXPERIMENTS_: Experiments,
        PathValues.EXPERIMENTS_UUID_: ExperimentsUuid,
        PathValues.FILES_: Files,
        PathValues.FILES_UUID_: FilesUuid,
        PathValues.FILES_UUID_REIMPORT_: FilesUuidReimport,
        PathValues.HARVEST_ERRORS_: HarvestErrors,
        PathValues.HARVEST_ERRORS_ID_: HarvestErrorsId,
        PathValues.HARVESTERS_: Harvesters,
        PathValues.HARVESTERS_UUID_: HarvestersUuid,
        PathValues.LABS_: Labs,
        PathValues.LABS_ID_: LabsId,
        PathValues.LOGIN_: Login,
        PathValues.MONITORED_PATHS_: MonitoredPaths,
        PathValues.MONITORED_PATHS_UUID_: MonitoredPathsUuid,
        PathValues.SCHEDULE_FAMILIES_: ScheduleFamilies,
        PathValues.SCHEDULE_FAMILIES_UUID_: ScheduleFamiliesUuid,
        PathValues.SCHEDULE_IDENTIFIERS_: ScheduleIdentifiers,
        PathValues.SCHEDULES_: Schedules,
        PathValues.SCHEDULES_UUID_: SchedulesUuid,
        PathValues.SCHEMA_VALIDATIONS_: SchemaValidations,
        PathValues.SCHEMA_VALIDATIONS_ID_: SchemaValidationsId,
        PathValues.TEAMS_: Teams,
        PathValues.TEAMS_ID_: TeamsId,
        PathValues.TOKENS_: Tokens,
        PathValues.TOKENS_ID_: TokensId,
        PathValues.UNITS_: Units,
        PathValues.UNITS_ID_: UnitsId,
        PathValues.USERS_: Users,
        PathValues.USERS_ID_: UsersId,
        PathValues.VALIDATION_SCHEMAS_: ValidationSchemas,
        PathValues.VALIDATION_SCHEMAS_UUID_: ValidationSchemasUuid,
        PathValues.VALIDATION_SCHEMAS_KEYS_: ValidationSchemasKeys,
    }
)

path_to_api = PathToApi(
    {
        PathValues.ACCESS_LEVELS_: AccessLevels,
        PathValues.ACTIVATE_: Activate,
        PathValues.CELL_CHEMISTRIES_: CellChemistries,
        PathValues.CELL_FAMILIES_: CellFamilies,
        PathValues.CELL_FAMILIES_UUID_: CellFamiliesUuid,
        PathValues.CELL_FORM_FACTORS_: CellFormFactors,
        PathValues.CELL_MANUFACTURERS_: CellManufacturers,
        PathValues.CELL_MODELS_: CellModels,
        PathValues.CELLS_: Cells,
        PathValues.CELLS_UUID_: CellsUuid,
        PathValues.CELLS_UUID_RDF_: CellsUuidRdf,
        PathValues.COLUMN_TYPES_: ColumnTypes,
        PathValues.COLUMN_TYPES_ID_: ColumnTypesId,
        PathValues.COLUMNS_: Columns,
        PathValues.COLUMNS_ID_: ColumnsId,
        PathValues.COLUMNS_ID_VALUES_: ColumnsIdValues,
        PathValues.CREATE_TOKEN_: CreateToken,
        PathValues.CYCLER_TESTS_: CyclerTests,
        PathValues.CYCLER_TESTS_UUID_: CyclerTestsUuid,
        PathValues.EQUIPMENT_: Equipment,
        PathValues.EQUIPMENT_UUID_: EquipmentUuid,
        PathValues.EQUIPMENT_FAMILIES_: EquipmentFamilies,
        PathValues.EQUIPMENT_FAMILIES_UUID_: EquipmentFamiliesUuid,
        PathValues.EQUIPMENT_MANUFACTURERS_: EquipmentManufacturers,
        PathValues.EQUIPMENT_MODELS_: EquipmentModels,
        PathValues.EQUIPMENT_TYPES_: EquipmentTypes,
        PathValues.EXPERIMENTS_: Experiments,
        PathValues.EXPERIMENTS_UUID_: ExperimentsUuid,
        PathValues.FILES_: Files,
        PathValues.FILES_UUID_: FilesUuid,
        PathValues.FILES_UUID_REIMPORT_: FilesUuidReimport,
        PathValues.HARVEST_ERRORS_: HarvestErrors,
        PathValues.HARVEST_ERRORS_ID_: HarvestErrorsId,
        PathValues.HARVESTERS_: Harvesters,
        PathValues.HARVESTERS_UUID_: HarvestersUuid,
        PathValues.LABS_: Labs,
        PathValues.LABS_ID_: LabsId,
        PathValues.LOGIN_: Login,
        PathValues.MONITORED_PATHS_: MonitoredPaths,
        PathValues.MONITORED_PATHS_UUID_: MonitoredPathsUuid,
        PathValues.SCHEDULE_FAMILIES_: ScheduleFamilies,
        PathValues.SCHEDULE_FAMILIES_UUID_: ScheduleFamiliesUuid,
        PathValues.SCHEDULE_IDENTIFIERS_: ScheduleIdentifiers,
        PathValues.SCHEDULES_: Schedules,
        PathValues.SCHEDULES_UUID_: SchedulesUuid,
        PathValues.SCHEMA_VALIDATIONS_: SchemaValidations,
        PathValues.SCHEMA_VALIDATIONS_ID_: SchemaValidationsId,
        PathValues.TEAMS_: Teams,
        PathValues.TEAMS_ID_: TeamsId,
        PathValues.TOKENS_: Tokens,
        PathValues.TOKENS_ID_: TokensId,
        PathValues.UNITS_: Units,
        PathValues.UNITS_ID_: UnitsId,
        PathValues.USERS_: Users,
        PathValues.USERS_ID_: UsersId,
        PathValues.VALIDATION_SCHEMAS_: ValidationSchemas,
        PathValues.VALIDATION_SCHEMAS_UUID_: ValidationSchemasUuid,
        PathValues.VALIDATION_SCHEMAS_KEYS_: ValidationSchemasKeys,
    }
)
