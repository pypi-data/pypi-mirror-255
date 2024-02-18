# do not import all endpoints into this module because that uses a lot of memory and stack frames
# if you need the ability to import all endpoints from this module, import them with
# from galv.apis.tag_to_api import tag_to_api

import enum


class TagValues(str, enum.Enum):
    ACCESS_LEVELS = "access_levels"
    ACTIVATE = "activate"
    CELL_CHEMISTRIES = "cell_chemistries"
    CELL_FAMILIES = "cell_families"
    CELL_FORM_FACTORS = "cell_form_factors"
    CELL_MANUFACTURERS = "cell_manufacturers"
    CELL_MODELS = "cell_models"
    CELLS = "cells"
    COLUMN_TYPES = "column_types"
    COLUMNS = "columns"
    CREATE_TOKEN = "create_token"
    CYCLER_TESTS = "cycler_tests"
    EQUIPMENT = "equipment"
    EQUIPMENT_FAMILIES = "equipment_families"
    EQUIPMENT_MANUFACTURERS = "equipment_manufacturers"
    EQUIPMENT_MODELS = "equipment_models"
    EQUIPMENT_TYPES = "equipment_types"
    EXPERIMENTS = "experiments"
    FILES = "files"
    HARVEST_ERRORS = "harvest_errors"
    HARVESTERS = "harvesters"
    LABS = "labs"
    LOGIN = "login"
    MONITORED_PATHS = "monitored_paths"
    SCHEDULE_FAMILIES = "schedule_families"
    SCHEDULE_IDENTIFIERS = "schedule_identifiers"
    SCHEDULES = "schedules"
    SCHEMA_VALIDATIONS = "schema_validations"
    TEAMS = "teams"
    TOKENS = "tokens"
    UNITS = "units"
    USERS = "users"
    VALIDATION_SCHEMAS = "validation_schemas"
