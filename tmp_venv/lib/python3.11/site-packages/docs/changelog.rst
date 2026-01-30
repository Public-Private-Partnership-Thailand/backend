Changelog
=========

0.7.0 (2025-08-25)
------------------

-  ``generate-pot-files``:

   -  Fix a 0.4.0 regression causing empty ``docs.pot`` files.
   -  Resolve the ``--versions-dir`` directory to avoid an exception.
   -  Log the extension version if the ``--verbose`` option is set.
   -  Pass the ``--verbose`` count (for example, ``-vv``) to Sphinx.

-  :class:`~ocdsextensionregistry.codelist_code.CodelistCode`: Add a :meth:`~ocdsextensionregistry.codelist_code.CodelistCode.__hash__` method.
-  Add support for Python 3.13.
-  Drop support for Python 3.9.

0.6.9 (2025-01-07)
------------------

-  :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder` also accepts ``standard_base_url`` as the bytes of a ZIP file.

0.6.8 (2024-12-17)
------------------

-  :meth:`~ocdsextensionregistry.versioned_release_schema.get_versioned_release_schema`: Handle extensions that set ``items`` to an array or omit ``$ref`` or ``items`` where these are expected.

0.6.7 (2024-12-15)
------------------

-  :meth:`~ocdsextensionregistry.versioned_release_schema.get_versioned_release_schema`: Copy schema before modifying in-place.

0.6.6 (2024-12-15)
------------------

-  :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`:

   -  :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.release_package_schema` and :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.record_package_schema`:

      -  Add ``proxies`` argument.
      -  Apply ``embed`` logic if ``patched`` argument is provided.

   -  :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.get_standard_file_contents` replaces ``{{lang}}`` and ``{{version}}`` in files.

0.6.5 (2024-12-14)
------------------

-  :meth:`ocdsextensionregistry.util.replace_refs`: Add ``keep_defs`` argument.

0.6.4 (2024-12-14)
------------------

-  :meth:`ocdsextensionregistry.util.replace_refs` no longer errors if ``definitions`` isn't set, like on the release package schema.

0.6.3 (2024-12-14)
------------------

-  :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`:

   -  :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.release_package_schema` and :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.record_package_schema`:

      -  Apply ``embed`` argument even if ``schema_base_url`` is not provided.
      -  Add ``patched`` argument, to skip :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.patched_release_schema`.
      -  Accept keyword arguments for :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.release_schema_patch`.

   -  :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.record_package_schema`:

      -  Patch the ``versionedRelease`` schema.

0.6.2 (2024-12-13)
------------------

-  :meth:`ocdsextensionregistry.util.replace_refs`: Accepts keyword arguments to pass through to ``jsonref.replace_refs``.

0.6.1 (2024-12-13)
------------------

-  :meth:`~ocdsextensionregistry.versioned_release_schema.get_versioned_release_schema`: Recognize the type ``["number", "string", "null"]``.

0.6.0 (2024-12-13)
------------------

-  Add :meth:`~ocdsextensionregistry.versioned_release_schema.get_versioned_release_schema`.
-  Add :meth:`ocdsextensionregistry.util.replace_refs`.
-  Prohibit extensions from using ``null`` to remove members.
-  When replacing ``$ref``'erences:

   -  Remove ``definitions``, as it is no longer relevant.
   -  Resolve only HTTP and HTTPS URLs, with a 10-second timeout.
   -  Merge properties that are siblings to the ``$ref`` property onto the referenced object.

0.5.5 (2024-11-25)
------------------

-  Set a User-Agent header on all requests.

0.5.4 (2024-10-27)
------------------

-  :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`: Add ``extension_value`` argument to :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.release_schema_patch` and :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.patched_release_schema`.

0.5.3 (2024-10-23)
------------------

-  Add ``patched-release-schema`` command.

0.5.2 (2024-10-21)
------------------

-  :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`:

   -  Revert "Disallow the ``file:`` scheme for the ``extension_versions`` argument." :commit:`097825c` :commit:`1012d2a`

-  :class:`~ocdsextensionregistry.extension_version.ExtensionVersion`:

   -  Allow URI schemes other than ``http`` and ``https`` by adding or replacing the :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.allow_schemes` `set <https://docs.python.org/3/tutorial/datastructures.html#sets>`__.
   -  Check URI schemes in :meth:`~ocdsextensionregistry.extension_version.ExtensionVersion.remote` and :meth:`~ocdsextensionregistry.extension_version.ExtensionVersion.zipfile`, to issue warnings before sending requests, not when initializing :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`.

0.5.1 (2024-10-21)
------------------

-  :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`: :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.extensions` raises :exc:`~ocdsextensionregistry.exceptions.UnsupportedSchemeError` instead of :exc:`NotImplementedError` if a URI scheme is not supported.

0.5.0 (2024-10-20)
------------------

-  Fix variable shadowing that prevented codelist translations.
-  :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`:

   -  Revert "The ``extension_versions`` argument can be a list of extensions' local directories" to eliminate possibility of malicious input reading local files. :commit:`7aba524`
   -  :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.extensions`: Disallow the ``file:`` scheme for the ``extension_versions`` argument.

0.4.0 (2024-09-15)
------------------

-  :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`: :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.release_package_schema` and :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.record_package_schema`: Some arguments must be keyword arguments.
-  Add support for Sphinx 7.
-  Drop support for Sphinx 4.
-  Drop support for Python 3.8.

0.3.8 (2023-07-20)
------------------

-  feat: :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`: The ``extension_versions`` argument can be a dict in which values are URLs, in addition to versions.

0.3.7 (2023-07-19)
------------------

-  feat: Change assertions to warnings, when adding or removing codes from an extension's codelist.

0.3.6 (2023-07-12)
------------------

-  fix: :class:`~ocdsextensionregistry.extension_version.ExtensionVersion`: Make :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.files`, :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.schemas`, :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.codelists` thread-safe.

0.3.5 (2023-07-12)
------------------

-  fix: :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`: Make :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.get_standard_file_contents` thread-safe.

0.3.4 (2023-07-08)
------------------

-  feat: :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder` also accepts ``standard_base_url`` as a ``file://`` URL to a ZIP file.

0.3.3 (2023-07-07)
------------------

-  feat: Make ExtensionVersion more robust to bad data, when using a package's ``extensions`` field as input.

   -  Warn if the request errors for an extension's codelist file (unreachable host, request timeout, HTTP error, too many redirects, etc.), if the bulk file isn't a ZIP file, or if the codelist isn't UTF-8.

      The previous behavior of raising an exception can be restored with:

      .. code-block:: python

         import warnings

         from ocdsextensionregistry.exceptions import ExtensionCodelistWarning


         with warnings.catch_warnings():
             warnings.filterwarnings('error', category=ExtensionCodelistWarning)
             # Use of ExtensionVersion.codelist that warns.

-  feat: Warn if the extension's release schema patch or codelist file isn't UTF-8.
-  feat: :class:`~ocdsextensionregistry.extension_version.ExtensionVersion`: Add :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.input_url` for the URL that was provided in a list to :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`'s :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.extensions`.
-  fix: :class:`~ocdsextensionregistry.extension_version.ExtensionVersion`: :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.repository_ref` only matches if the extension's files are in the repository's root – which is required by :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.repository_ref_download_url`.

0.3.2 (2023-07-07)
------------------

-  :class:`~ocdsextensionregistry.extension_version.ExtensionVersion`:

   -  feat: Add :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.repository_ref` and :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.repository_ref_download_url`.
   -  feat: Set :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.download_url` to :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.repository_ref_download_url` on initialization, if possible.

0.3.1 (2023-07-07)
------------------

-  fix: :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`: :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.extensions`: Support retrieval of the metadata file, if the ``extension_versions`` argument is a list of extensions' metadata files served via API.

0.3.0 (2023-07-06)
------------------

-  feat: Make ProfileBuilder more robust to bad data, when using a package's ``extensions`` field as input.

   -  Skip a package's ``extensions`` field if it is not an array.
   -  Skip an entry in the package's ``extensions`` array if it is blank or is not a string.
   -  Warn if the request errors for the extension's release schema patch (unreachable host, request timeout, HTTP error, too many redirects, etc.), if the bulk file is not a ZIP file, or if the release schema is not a JSON file.

      The previous behavior of raising an exception can be restored with:

      .. code-block:: python

         import warnings

         from ocdsextensionregistry.exceptions import ExtensionWarning


         with warnings.catch_warnings():
             warnings.filterwarnings('error', category=ExtensionWarning)
             # Use of ProfileBuilder.release_schema_path() that warns.

-  feat: Configure the expiration behavior of the responses cache using a ``REQUESTS_CACHE_EXPIRE_AFTER`` environment variable. See `requests-cache's documentation <https://requests-cache.readthedocs.io/en/stable/user_guide/expiration.html>`__ (``NEVER_EXPIRE`` is ``-1`` and ``EXPIRE_IMMEDIATELY`` is ``0``, in the `source <https://github.com/requests-cache/requests-cache/blob/main/requests_cache/policy/expiration.py>`__).
-  :class:`~ocdsextensionregistry.extension_version.ExtensionVersion`:

   -  fix: :meth:`~ocdsextensionregistry.extension_version.ExtensionVersion.__repr__` no longer errors if initialized with ``file_urls`` only.
   -  fix: :meth:`~ocdsextensionregistry.extension_version.ExtensionVersion.get_url` raises clearer error if initialized with a Download URL only.

-  Add support for Sphinx 6.2 on Python 3.11.

0.2.2 (2023-06-05)
------------------

-  :class:`~ocdsextensionregistry.extension_version.ExtensionVersion`:

   -  fix: :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.repository_full_name` and :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.repository_name` return the correct name for GitLab URLs.
   -  fix: Clarify error message for ``AttributeError`` on :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.repository_full_name`, :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.repository_name`, and :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.repository_user`.

0.2.1 (2023-05-24)
------------------

-  feat: Add a ``--no-frozen`` option to all commands.
-  Drop support for Python 3.7.

0.2.0 (2022-10-29)
------------------

-  fix: :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`: :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.release_package_schema` and :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.record_package_schema` return a JSON-serializable object when ``embed=True``.

0.1.14 (2022-09-07)
-------------------

-  fix: Skip version of ``cattrs`` that fails on PyPy.

0.1.13 (2022-06-20)
-------------------

-  feat: :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`: The ``extension_versions`` argument can be a list of extensions' metadata files served via API.

0.1.12 (2022-04-06)
-------------------

-  ``generate-pot-files``: Drop support for Sphinx<4.3, before which Python 3.10 is unsupported.
-  fix: Ignore ResourceWarning from `requests-cache <https://requests-cache.readthedocs.io/en/stable/user_guide/troubleshooting.html#common-error-messages>`__.

0.1.11 (2022-02-01)
-------------------

-  feat: Retry requests up to 3 times.

0.1.10 (2022-01-31)
-------------------

-  feat: :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`: The ``extension_versions`` argument can be a list of extensions' release schema patch files.

0.1.9 (2022-01-24)
------------------

-  fix: Convert the ``REQUESTS_POOL_MAXSIZE`` environment variable to ``int``.

0.1.8 (2022-01-20)
------------------

-  fix: Fix the default value for an extension's ``release-schema.json`` file (``{}``).

0.1.7 (2022-01-12)
------------------

-  feat: Use the ``REQUESTS_POOL_MAXSIZE`` environment variable to set the maximum number of connections to save in the `connection pool <https://urllib3.readthedocs.io/en/latest/advanced-usage.html#customizing-pool-behavior>`__.
-  Drop support for Python 3.6.

0.1.6 (2021-11-29)
------------------

-  feat: :class:`~ocdsextensionregistry.extension_version.ExtensionVersion`: :meth:`~ocdsextensionregistry.extension_version.ExtensionVersion.remote` returns the ``default`` argument, if provided, if the file does not exist. :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`'s :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.release_schema_patch` uses a default of ``{}`` for ``release-schema.json``.

0.1.5 (2021-11-24)
------------------

-  Do not patch ``requests`` to cache responses.

0.1.4 (2021-04-10)
------------------

-  Add Python wheels distribution.

0.1.3 (2021-03-05)
------------------

-  ``generate-pot-files``: Add ``-W`` option to turn Sphinx warnings into errors, for debugging.

0.1.2 (2021-02-19)
------------------

-  :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`: :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.release_schema_patch` and :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.patched_release_schema`: Add a ``language`` argument to set the language to use for the name of the extension.

0.1.1 (2021-02-17)
------------------

-  ``generate-data-file``: Use Authorization header instead of ``access_token`` query string parameter to authenticate with GitHub.

0.1.0 (2021-02-16)
------------------

-  Switch to MyST-Parser from recommonmark.
-  Drop support for Sphinx directives.

0.0.26 (2021-02-16)
-------------------

-  :meth:`ocdsextensionregistry.util.get_latest_version`: If an extension has no "master" version, check for a "1.1" version.

0.0.25 (2021-02-12)
-------------------

-  :class:`~ocdsextensionregistry.codelist.Codelist`: Add :meth:`~ocdsextensionregistry.codelist.Codelist.to_csv` and :meth:`~ocdsextensionregistry.codelist.Codelist.__lt__`.
-  :class:`~ocdsextensionregistry.codelist_code.CodelistCode`: Add :meth:`~ocdsextensionregistry.codelist_code.CodelistCode.__lt__`.

0.0.24 (2020-09-12)
-------------------

-  :class:`~ocdsextensionregistry.extension_registry.ExtensionRegistry`: Add :meth:`~ocdsextensionregistry.extension_registry.ExtensionRegistry.get_from_url`.
-  :class:`~ocdsextensionregistry.extension_version.ExtensionVersion`: Add :meth:`~ocdsextensionregistry.extension_version.ExtensionVersion.get_url`.
-  :meth:`~ocdsextensionregistry.api.build_profile` aggregates ``dependencies`` and ``testDependencies`` from extensions.

0.0.23 (2020-08-20)
-------------------

-  :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`: :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.get_standard_file_contents`: Fix for OCDS 1.1.5.

0.0.22 (2020-08-11)
-------------------

-  :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`:

   -  No longer errors if ``standard_tag`` argument is ``None``.
   -  :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.release_schema_patch`: Only annotates definitions and fields with ``title`` properties.

0.0.21 (2020-07-22)
-------------------

-  :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`:

   -  The ``extension_versions`` argument can be a list of extensions' local directories.
   -  Add a ``standard_base_url`` argument, which can be a ``file://`` URL to the standard's directory.
   -  Add :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.record_package_schema` method, to match :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.release_package_schema`.
   -  :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.release_package_schema`: Add a ``embed`` argument to indicate whether to embed the patched release schema in the release package schema.

-  :class:`~ocdsextensionregistry.extension_version.ExtensionVersion`:

   -  Remove ``available_in_bulk()`` method.
   -  Remove ``directory`` property (overload ``download_url`` instead).

-  :meth:`~ocdsextensionregistry.api.build_profile`: Add a ``standard_base_url`` argument to modify the standard base URL.

0.0.20 (2020-06-08)
-------------------

-  Add Windows support for:

   -  :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`: :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.get_standard_file_contents`
   -  :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`: :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.standard_codelists`
   -  :class:`~ocdsextensionregistry.extension_version.ExtensionVersion`: :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.files`

0.0.19 (2020-04-07)
-------------------

-  The ``generate-data-file`` command warns if an MO file is missing.
-  Rename environment variable from ``GITHUB_ACCESS_TOKEN`` to ``OCDS_GITHUB_ACCESS_TOKEN``.

0.0.18 (2020-04-06)
-------------------

-  The ``generate-data-file`` command uses a null translator if an MO file is missing.
-  :class:`~ocdsextensionregistry.extension_version.ExtensionVersion`: :meth:`~ocdsextensionregistry.extension_version.ExtensionVersion.__repr__` falls back to Base URL and Download URL if Id or Version is blank.

0.0.17 (2020-04-03)
-------------------

-  :class:`~ocdsextensionregistry.extension_version.ExtensionVersion`:

   -  Add :meth:`~ocdsextensionregistry.extension_version.ExtensionVersion.__repr__`.
   -  :meth:`~ocdsextensionregistry.extension_version.ExtensionVersion.remote` raises :exc:`~ocdsextensionregistry.exceptions.DoesNotExist` instead of :exc:`KeyError` if a file does not exist.

-  :class:`~ocdsextensionregistry.extension.Extension`: Add :meth:`~ocdsextensionregistry.extension.Extension.__repr__`.

0.0.16 (2019-11-20)
-------------------

-  Add support for Sphinx>=1.6.

0.0.15 (2019-09-30)
-------------------

-  :meth:`~ocdsextensionregistry.api.build_profile`: Add a ``update_codelist_urls`` argument to modify codelist reference URLs.

0.0.14 (2019-09-18)
-------------------

-  Use in-memory cache for HTTP responses.

0.0.13 (2019-08-29)
-------------------

-  :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`: :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.release_package_schema` and :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.patched_release_schema`: Add a ``schema`` argument to override the release schema or release package schema.

0.0.12 (2019-08-29)
-------------------

-  :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`:

   -  Unregistered extensions are now supported by the profile builder. The ``extension_versions`` argument can be a list of extensions' metadata URLs, base URLs and/or download URLs.
   -  Add an ``extension_field`` argument to :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.release_schema_patch` and :meth:`~ocdsextensionregistry.profile_builder.ProfileBuilder.patched_release_schema` methods to annotate all definitions and fields with extension names.

-  Add :meth:`ocdsextensionregistry.util.get_latest_version`, to return the identifier of the latest version from a list of versions of the same extension.

0.0.11 (2019-06-26)
-------------------

-  The ``generate-pot-files`` and ``generate-data-file`` commands can now be run offline (see `documentation <https://ocdsextensionregistry.readthedocs.io/en/latest/cli.html>`__ for details).
-  Add a ``--versions-dir`` option to the ``generate-pot-files`` and ``generate-data-file`` commands to specify a local directory of extension versions.
-  :class:`~ocdsextensionregistry.extension_registry.ExtensionRegistry`: Support the ``file://`` scheme for the ``extension_versions_data`` and ``extensions_data`` arguments. This means the ``--extension-versions-url`` and ``--extensions-url`` CLI options can now refer to local files.
-  :class:`~ocdsextensionregistry.extension_version.ExtensionVersion`:

   -  Add ``available_in_bulk()``, to return whether the extension’s files are available in bulk.
   -  Add :meth:`~ocdsextensionregistry.extension_version.ExtensionVersion.zipfile`, to return a ZIP archive of the extension’s files.
-  Upgrade to ocds-babel 0.1.0.

0.0.10 (2019-01-28)
-------------------

-  :class:`~ocdsextensionregistry.extension_version.ExtensionVersion`: :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.metadata`: Fix invalid ``dependencies`` in ``extension.json``.

0.0.9 (2019-01-23)
------------------

-  ``generate-pot-files``: Drop support for ``docs/`` directory in extensions.
-  :class:`~ocdsextensionregistry.extension_version.ExtensionVersion`: Remove ``docs`` property.
-  :meth:`~ocdsextensionregistry.api.build_profile`:

   -  Use UTF-8 characters in JSON files.
   -  No longer write extension readme files.

0.0.8 (2019-01-18)
------------------

-  ``generate-data-file``: Fix rate limiting error when getting publisher names from GitHub.

0.0.7 (2019-01-18)
------------------

-  ``generate-data-file``: Add ``publisher`` data.
-  :class:`~ocdsextensionregistry.extension_version.ExtensionVersion`: Add :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.repository_user` and :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.repository_user_page` properties, to return user or organization to which the extension’s repository belongs.

0.0.6 (2018-11-20)
------------------

-  Add command-line tools (see `documentation <https://ocdsextensionregistry.readthedocs.io/en/latest/cli.html>`__ for details).
-  :class:`~ocdsextensionregistry.extension_version.ExtensionVersion`: Fix edge case so that :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.metadata` language maps are ordered, even if ``extension.json`` didn’t have language maps.

0.0.5 (2018-10-31)
------------------

-  Add  :class:`~ocdsextensionregistry.profile_builder.ProfileBuilder`, :class:`~ocdsextensionregistry.codelist.Codelist`, :class:`~ocdsextensionregistry.codelist_code.CodelistCode` classes.
-  :class:`~ocdsextensionregistry.extension_version.ExtensionVersion`:

   -  Add :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.files` property, to return the contents of all files within the extension.
   -  Add :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.schemas` property, to return the schemas.
   -  Add :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.codelists` property, to return the codelists.
   -  Add ``docs`` property, to return the contents of documentation files within the extension.
   -  The :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.metadata` property normalizes the contents of ``extension.json`` to provide consistent access.

0.0.4 (2018-06-27)
------------------

-  :class:`~ocdsextensionregistry.extension_version.ExtensionVersion`: The :attr:`~ocdsextensionregistry.extension_version.ExtensionVersion.metadata` property is cached.

0.0.3 (2018-06-27)
------------------

-  :class:`~ocdsextensionregistry.extension_version.ExtensionVersion`:

   -  Add :meth:`~ocdsextensionregistry.extension_version.ExtensionVersion.remote` method, to return the contents of a file within the extension.
   -  Add :meth:`~ocdsextensionregistry.extension_version.ExtensionVersion.as_dict` method, to avoid returning private properties.

-  :class:`~ocdsextensionregistry.extension.Extension`: Add :meth:`~ocdsextensionregistry.extension.Extension.as_dict` method, to avoid returning private properties.

0.0.2 (2018-06-12)
------------------

-  :class:`~ocdsextensionregistry.extension_registry.ExtensionRegistry`:

   -  Add :meth:`~ocdsextensionregistry.extension_registry.ExtensionRegistry.get` method, to get a specific extension version.
   -  Add :meth:`~ocdsextensionregistry.extension_registry.ExtensionRegistry.__iter__` method, to iterate over all extension versions.
   -  Remove ``all()`` method.

-  Add package-specific :doc:`api/exceptions`.

0.0.1 (2018-06-11)
------------------

First release.
