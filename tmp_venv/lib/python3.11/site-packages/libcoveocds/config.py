import copy

LIB_COVE_OCDS_CONFIG_DEFAULT = {
    # SchemaOCDS options
    # Note: "schema_version" is set after this dict.
    #
    # Used by lib-cove in common_checks_context() via SchemaOCDS for "version_display_choices", "version_used_display".
    "schema_version_choices": {
        # version: (display, url, tag),
        "1.0": ("1.0", "https://standard.open-contracting.org/1.0/en/", "1__0__3"),
        "1.1": ("1.1", "https://standard.open-contracting.org/1.1/en/", "1__1__5"),
    },
    # Used by lib-cove in get_additional_codelist_values() via SchemaOCDS for "codelist_url".
    "schema_codelists": {
        # version: codelist_dir,
        "1.1": "https://raw.githubusercontent.com/open-contracting/standard/1.1/schema/codelists/",
    },
    # The language key to use to read extension metadata.
    "current_language": "en",
    # Path to ZIP file of standard repository.
    "standard_zip": None,
    #
    # Flatten Tool options
    #
    # Used by lib-cove in convert_spreadsheet() and convert_json() via ocds_json_output().
    "root_list_path": "releases",
    "root_id": "ocid",
    "convert_titles": False,
    "flatten_tool": {
        "disable_local_refs": True,
        "remove_empty_schema_columns": True,
    },
    #
    # lib-cove-ocds options
    #
    # Which additional checks to perform ("all" or "none", per libcoveocds.lib.additional_checks.CHECKS).
    "additional_checks": "all",
    # Whether to add "releases_aggregates" and "records_aggregates" to the context.
    "skip_aggregates": False,
    # The context in which lib-cove-ocds is used ("web" or "api").
    "context": "web",
}

# Set default schema version to the latest version
LIB_COVE_OCDS_CONFIG_DEFAULT["schema_version"] = list(LIB_COVE_OCDS_CONFIG_DEFAULT["schema_version_choices"])[-1]


class LibCoveOCDSConfig:
    def __init__(self, config=None):
        self.config = copy.deepcopy(LIB_COVE_OCDS_CONFIG_DEFAULT)
        if config:
            self.config.update(config)
