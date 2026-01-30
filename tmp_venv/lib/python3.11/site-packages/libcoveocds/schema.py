import functools
import json
import logging
import os
import warnings
import zipfile
from collections import defaultdict
from copy import deepcopy
from urllib.parse import urljoin

import jsonref
import requests
from libcove.lib.common import get_schema_codelist_paths, schema_dict_fields_generator
from ocdsextensionregistry.exceptions import DoesNotExist, ExtensionCodelistWarning, ExtensionWarning
from ocdsextensionregistry.profile_builder import ProfileBuilder
from referencing import Registry, Resource

import libcoveocds.config
from libcoveocds.exceptions import OCDSVersionError

logger = logging.getLogger(__name__)


# Note: Using lru_cache on instance methods can lead to memory leaks. However, we generally do want these to survive
# the entire process.
# https://beta.ruff.rs/docs/rules/cached-instance-method/
class SchemaOCDS:
    def __init__(self, select_version=None, package_data=None, lib_cove_ocds_config=None, *, record_pkg=False):
        """
        Build the schema object using an specific OCDS schema version.

        The version used will be select_version, package_data.get('version') or
        default version, in that order. Invalid version choices in select_version or
        package_data will be skipped and registered as self.invalid_version_argument
        and self.invalid_version_data respectively.
        """
        # The main configuration object.
        self.config = lib_cove_ocds_config or libcoveocds.config.LibCoveOCDSConfig()
        # Whether used in an API context.
        self.api = self.config.config["context"] == "api"

        # lib-cove uses codelists in get_additional_codelist_values() for "codelist_url".
        self.codelists = self.config.config["schema_codelists"]["1.1"]
        # lib-cove uses version_choices in common_checks_context() via getattr() for "version_display_choices" and
        # "version_used_display". Re-used in this file for convenience.
        self.version_choices = self.config.config["schema_version_choices"]
        # lib-cove uses version in common_checks_context() via getattr() to determine whether to set
        # "version_display_choices" and "version_used_display".
        # cove-ocds uses version, e.g. when a user changes the version to validate against.
        self.version = self.config.config["schema_version"]

        # Report errors in web UI.
        self.missing_package = False
        self.json_deref_error = None  # str
        # Errors are raised instead in API context.
        self.invalid_version_argument = False
        self.invalid_version_data = False

        # The selected version overrides the default version and the data version.
        if select_version:
            if select_version in self.version_choices:
                self.version = select_version
            elif self.api:
                raise OCDSVersionError(
                    f"select_version: {select_version} is not one of {', '.join(self.version_choices)}"
                )
            else:
                self.invalid_version_argument = True
                # If invalid, use other strategies.
                select_version = None

        # lib-cove uses extensions in common_checks_context() for "extensions"."extensions".
        # If `self.extensions` is falsy, this logic can be skipped.
        # cove-ocds uses extensions to render extension-related information.
        self.extensions = {}
        if isinstance(package_data, dict):
            if "releases" not in package_data and "records" not in package_data:
                self.missing_package = True
            if not select_version and "version" in package_data:
                package_version = package_data["version"]
                if not isinstance(package_version, str):
                    self.invalid_version_data = True
                elif package_version:
                    if package_version in self.version_choices:
                        self.version = package_version
                    elif self.api:
                        raise OCDSVersionError(
                            f"The version in the data is not one of {', '.join(self.version_choices)}"
                        )
                    else:
                        self.invalid_version_data = True

            extensions = package_data.get("extensions")
            if isinstance(extensions, list):
                self.extensions = {extension: {} for extension in extensions if isinstance(extension, str)}

        base_url = self.version_choices[self.version][1]
        # cove-ocds and the CLI uses schema_url as a fallback to extended_schema_file, to convert between formats.
        self.schema_url = urljoin(base_url, "release-schema.json")
        # Used in get_pkg_schema_obj() to determine which package to return.
        if record_pkg:
            self.package_schema_name = "record-package-schema.json"
        else:
            self.package_schema_name = "release-package-schema.json"
        # lib-cove uses pkg_schema_url in common_checks_context() for "schema_url".
        self.pkg_schema_url = urljoin(base_url, self.package_schema_name)

        tag = self.version_choices[self.version][2]
        #: The profile builder instance for this package's extensions.
        self.builder = ProfileBuilder(tag, list(self.extensions), standard_base_url=self.config.config["standard_zip"])
        # Initialize extensions once and preserve locale caches.
        self.builder_extensions = list(self.builder.extensions())

        # lib-cove uses extended in common_checks_context() for "extensions"."is_extended_schema".
        # If `self.extensions` is falsy, this logic can be skipped.
        # cove-ocds uses is_extended_schema to conditionally display content.
        self.extended = False
        # lib-cove uses invalid_extension in common_checks_context() for "extensions"."invalid_extension".
        # If `self.extensions` is falsy, this logic can be skipped.
        # cove-ocds uses invalid_extension to render extension-related errors.
        self.invalid_extension = {}

        # lib-cove uses extended_schema_url in common_checks_context() for "extensions"."extended_schema_url".
        # If `self.extensions` is falsy, this logic can be skipped.
        # cove-ocds uses extended_schema_url to "Get a copy of the schema with extension patches applied".
        self.extended_schema_url = None
        # lib-cove uses extended_schema_file in get_schema_validation_errors() to call CustomRefResolver(), if extended
        # is set. The CLI uses extended_schema_file to convert between formats, and falls back to schema_url.
        self.extended_schema_file = None

    @staticmethod
    def _codelist_codes(codelist):
        if not codelist.rows:
            return set()
        column = next(column for column in ("Code", "Código", "code") if column in codelist.rows[0])
        return {row[column] for row in codelist.rows}

    def _standard_codelists(self):
        try:
            # OCDS 1.0 uses "code" column.
            # https://github.com/open-contracting/standard/blob/1__0__3/standard/schema/codelists/organizationIdentifierRegistrationAgency_iati.csv
            return {codelist.name: self._codelist_codes(codelist) for codelist in self.builder.standard_codelists()}
        except requests.RequestException:
            logger.exception()
            return {}

    # Override
    #
    # lib-cove calls this from get_additional_codelist_values().
    @functools.lru_cache  # noqa: B019
    def process_codelists(self):
        # lib-cove uses these in get_additional_codelist_values().
        # - Used to determine whether a field has a codelist, which codelist and whether it is open.
        self.extended_codelist_schema_paths = get_schema_codelist_paths(self, use_extensions=True)
        # - Used with the `in` operator, to determine whether a codelist is from an extension.
        self.core_codelists = self._standard_codelists()
        # - Used with get(), and the return value is used with `in`, to determine whether a code is included.
        self.extended_codelists = deepcopy(self.core_codelists)
        # - Used to populate "codelist_url" and "codelist_amend_urls".
        self.extended_codelist_urls = defaultdict(list)

        # _standard_codelists() returns an empty dict on HTTP error. If so, don't cache this empty dict, and return.
        if not self.core_codelists:
            self._standard_codelists.cache_clear()
            return

        for extension in self.builder_extensions:
            input_url = extension.input_url

            failed_codelists = self.extensions[input_url].get("failed_codelists")

            # In a web context, skip extensions whose metadata is unavailable.
            if failed_codelists is None:
                continue

            with warnings.catch_warnings(record=True) as wlist:
                warnings.simplefilter("always", category=ExtensionCodelistWarning)

                try:
                    # An unreadable metadata file or a malformed extension URL raises an error.
                    extension_codelists = extension.codelists
                except (requests.RequestException, NotImplementedError):
                    # patched_release_schema() will have recorded the metadata file being unreadable.
                    continue

            for w in wlist:
                if issubclass(w.category, ExtensionCodelistWarning):
                    exception = w.message.exc
                    if isinstance(exception, requests.HTTPError):
                        message = f"{exception.response.status_code}: {exception.response.reason}"
                    elif isinstance(exception, (requests.RequestException, zipfile.BadZipFile)):
                        message = "Couldn't be retrieved"
                    elif isinstance(exception, UnicodeDecodeError):
                        message = "Has non-UTF-8 characters"
                    else:
                        message = f"Unknown error: {exception}"
                    failed_codelists[w.message.codelist] = message
                else:
                    warnings.warn_explicit(w.message, w.category, w.filename, w.lineno, source=w.source)

            for name, codelist in extension_codelists.items():
                try:
                    codes = self._codelist_codes(codelist)
                except StopIteration:
                    failed_codelists[name] = 'Has no "Code" column'
                    continue

                if codelist.patch:
                    basename = codelist.basename

                    if basename not in self.core_codelists:
                        failed_codelists[name] = f"References non-existing codelist {basename}"
                        continue

                    patched_codelist = self.extended_codelists[basename]

                    if codelist.addend:
                        patched_codelist |= codes
                    elif codelist.subtrahend:
                        nonexisting_codes = [code for code in codes if code not in patched_codelist]
                        if nonexisting_codes:
                            failed_codelists[name] = f"References non-existing code(s): {', '.join(nonexisting_codes)}"
                        patched_codelist -= codes
                else:
                    self.extended_codelists[name] = codes

                self.extended_codelist_urls[name].append(extension.get_url(f"codelists/{name}"))

    # lib-cove's get_schema_validation_errors() uses this, if defined. This circumvents CustomRefResolver() logic.
    @functools.lru_cache  # noqa: B019
    def validator(self, validator, format_checker):
        return validator(self.get_pkg_schema_obj(), format_checker=format_checker, registry=self.registry)

    @functools.cached_property
    def registry(self):
        # lib-cove's get_schema_validation_errors() expects a non-dereferenced schema.
        # The cove-ocds test with tenders_releases_1_release_with_extension_broken_json_ref.json fails, otherwise.
        release_schema = self.get_schema_obj()
        # get_schema_validation_errors() needs "isCodelist" properties. See _add_is_codelist(). This property is
        # undesirable elsewhere, like in create_extended_schema_file().
        self._add_is_codelist(release_schema)

        versioned_release_schema = json.loads(
            self.builder.get_standard_file_contents("versioned-release-validation-schema.json")
        )

        tag = self.version_choices[self.version][2]

        return Registry().with_resources(
            [
                (f"{scheme}://standard.open-contracting.org/schema/{tag}/{prefix}-schema.json", schema)
                # OCDS 1.0 use the http scheme.
                for scheme in ("http", "https")
                for prefix, schema in (
                    ("release", Resource.from_contents(release_schema)),
                    ("versioned-release-validation", Resource.from_contents(versioned_release_schema)),
                )
            ]
        )

    # For array codelist fields, the `codelist` custom validation keyword is set on the array field, rather than on the
    # `items` subschema. cove-ocds needs to report codelist errors separately from other structural errors. However,
    # the errors returned by jsonschema to get_schema_validation_errors() don't provide access to an `items` parent
    # schema. So, we add a sentinel keyword to the `items` subschema.
    #
    # It is necessary to add it to string codelist fields, too, because lib-cove checks for "isCodelist" only.
    #
    # For reference, the original commit:
    # https://github.com/OpenDataServices/cove/commit/b0591da69cae8258c7029d11e22297d86e6b98c3
    @staticmethod
    def _add_is_codelist(subschema: dict) -> None:
        for value in subschema.get("properties", {}).values():
            if not isinstance(value, dict):
                continue

            types = value.get("type", [])
            if not isinstance(types, list):
                types = [types]

            # get_schema_codelist_paths() defaults "openCodelist" to false.
            if "array" in types:
                if isinstance(value.get("items"), dict):
                    if "codelist" in value and value.get("openCodelist", False) is False:
                        value["items"]["isCodelist"] = True
                    SchemaOCDS._add_is_codelist(value["items"])
            else:
                if "codelist" in value and value.get("openCodelist", False) is False:
                    value["isCodelist"] = True
                if "object" in types:
                    SchemaOCDS._add_is_codelist(value)

        for value in subschema.get("definitions", {}).values():
            if not isinstance(value, dict):
                continue
            SchemaOCDS._add_is_codelist(value)

    def _get_schema(self, name):
        # The ocds_babel.translate.translate() makes these substitutions for published files.
        return json.loads(
            self.builder.get_standard_file_contents(name)
            .replace("{{lang}}", self.config.config["current_language"])
            .replace("{{version}}", self.version)
        )

    # Preserve "deprecated" as a sibling of "$ref", via either `merge_props=True` or `proxies=True`.
    #
    # Proxies are required for libcoveocds.common_checks_lookup_schema() to determine the URL fragments for
    # definitions' fields (though `docs_ref` is not used in cove-ocds).
    # https://github.com/open-contracting/cove-ocds/issues/103
    @staticmethod
    def _jsonref_kwarg(*, proxies=False):
        if proxies:
            return {"proxies": True, "lazy_load": False}
        return {"proxies": False, "merge_props": True}

    # Override
    #
    # lib-cove calls this from many locations including get_schema_validation_errors().
    #
    # All callers set use_extensions=True, so it is ignored.
    #
    # ProfileBuilder.release_package_schema() and record_package_schema() aren't used, because the patched release
    # schema has already been calculated and cached by patched_release_schema().
    @functools.lru_cache  # noqa: B019
    def get_pkg_schema_obj(self, *, deref=False, use_extensions=True, proxies=False):  # noqa: ARG002 # lib-cove API
        # For tests only.
        if hasattr(self, "_test_override_package_schema"):
            with open(self._test_override_package_schema) as f:
                if deref:
                    return jsonref.load(f, **self._jsonref_kwarg(proxies=proxies))
                return json.load(f)
        else:
            schema = self._get_schema(self.package_schema_name)

        if deref:
            patched = self.get_schema_obj(deref=True, proxies=proxies)
            if self.package_schema_name == "record-package-schema.json":
                schema["definitions"]["record"]["properties"]["compiledRelease"] = patched
                schema["definitions"]["record"]["properties"]["releases"]["oneOf"][1]["items"] = patched
                # The Record definition must be dereferenced for "additional_fields" to report correctly.
                # Can test with tenders_records_1_record_with_invalid_extensions.json in cove-ocds.
                schema = jsonref.replace_refs(schema, **self._jsonref_kwarg(proxies=proxies))
            else:
                schema["properties"]["releases"]["items"] = patched

        return schema

    # Override
    @functools.lru_cache  # noqa: B019
    def get_schema_obj(self, *, deref=False, proxies=False):
        with warnings.catch_warnings(record=True) as wlist:
            warnings.simplefilter("always", category=ExtensionWarning)

            schema = self.builder.patched_release_schema(schema=self._get_schema("release-schema.json"))
            if deref:
                try:
                    schema = jsonref.replace_refs(schema, **self._jsonref_kwarg(proxies=proxies))
                except jsonref.JsonRefError as e:
                    # Callers must check json_deref_error.
                    self.json_deref_error = e.message
                    # This is the prior behavior, however surprising.
                    # https://github.com/OpenDataServices/lib-cove/blob/a97f769/libcove/lib/common.py#L393-L405
                    schema = {}

        for w in wlist:
            if issubclass(w.category, ExtensionWarning):
                exception = w.message.exc
                if isinstance(exception, requests.HTTPError):
                    message = f"{exception.response.status_code}: {exception.response.reason.lower()}"
                elif isinstance(exception, (requests.RequestException, zipfile.BadZipFile)):
                    message = "fetching failed"
                elif isinstance(exception, json.JSONDecodeError):
                    message = "release schema patch is not valid JSON"
                else:
                    message = str(exception)
                self.invalid_extension[w.message.extension.input_url] = message
            else:
                warnings.warn_explicit(w.message, w.category, w.filename, w.lineno, source=w.source)

        language = self.config.config["current_language"]

        for extension in self.builder_extensions:
            input_url = extension.input_url

            # process_codelists() needs this dict.
            details = {"url": input_url, "failed_codelists": {}}

            # Skip metadata fields in API context.
            if self.api:
                self.extensions[input_url] = details
                continue

            # Presence checked in cove-ocds templates.
            details["schema_url"] = None

            # ocdsextensionregistry requires the input URL to contain "extension.json" (like the registry). If it
            # doesn't, ocdsextensionregistry can't determine how to retrieve it.
            if not extension.base_url and not extension._url_pattern:  # noqa: SLF001
                self.invalid_extension[input_url] = "missing extension.json"
                continue

            try:
                metadata = extension.metadata

                # We *could* check its existence via HTTP, but this is for display only anyway.
                schemas = metadata.get("schemas")
                if isinstance(schemas, list) and "release_schema.json" in schemas:
                    details["schema_url"] = extension.get_url("release-schema.json")

                for field in ("name", "description", "documentationUrl"):
                    language_map = metadata[field]
                    details[field] = language_map.get(language, language_map.get("en", ""))

                # In a web context, set the details only if metadata is available, otherwise cove-ocds' present
                # behavior to create an empty list item for the extension.
                self.extensions[input_url] = details
            except DoesNotExist:
                self.invalid_extension[input_url] = "404: not found"
            except requests.HTTPError as e:
                self.invalid_extension[input_url] = f"{e.response.status_code}: {e.response.reason.lower()}"
            except requests.RequestException:
                self.invalid_extension[input_url] = "fetching failed"
            except json.JSONDecodeError:
                self.invalid_extension[input_url] = "extension metadata is not valid JSON"

        # It's possible for the release schema to be applied, but the metadata file to be unavailable.
        # Nonetheless, for now, preserve prior behavior by reporting as if it were not applied.
        self.extended = len(self.invalid_extension) < len(self.extensions)

        return schema

    # Override
    #
    # Add decorator to copy from libcove.lib.common.SchemaJsonMixin.
    @functools.lru_cache  # noqa: B019
    def get_pkg_schema_fields(self):
        return set(schema_dict_fields_generator(self.get_pkg_schema_obj(deref=True)))

    # This is always called with an `if schema_ocds.extensions` guard.
    def create_extended_schema_file(self, upload_dir, upload_url):
        basename = "extended_schema.json"
        path = os.path.join(upload_dir, basename)

        # Always replace any existing extended schema file
        if os.path.exists(path):
            os.remove(path)
            self.extended_schema_file = None
            self.extended_schema_url = None

        schema = self.get_schema_obj()
        if not self.extended:
            return

        with open(path, "w") as f:
            json.dump(schema, f, ensure_ascii=False, indent=2)
            f.write("\n")
        self.extended_schema_file = path
        self.extended_schema_url = urljoin(upload_url, basename)
