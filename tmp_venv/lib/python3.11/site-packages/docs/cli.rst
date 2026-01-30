Command-Line Interface
======================

To install this package with command-line tools, run:

.. code-block:: bash

   pip install ocdsextensionregistry[cli]

To see all commands available, run:

.. code-block:: bash

   ocdsextensionregistry --help

If you see a message at the start of the output like:

.. code-block:: none

   exception "No module named 'babel'" prevented loading of ocdsextensionregistry.commands.generate_pot_files module

then you installed ``ocdsextensionregistry`` without command-line tools. To fix this, install as above.

patched-release-schema
----------------------

Create a patched release schema from the extensions array of a release package or record package.

.. code-block:: bash

  ocdsextensionregistry patched-release-schema my-release-package.json

download
--------

Download versions of extensions to a local directory.

To download all versions of all extensions into an ``outputdir`` directory:

.. code-block:: bash

   ocdsextensionregistry download outputdir

To download all versions of specific extensions:

.. code-block:: bash

   ocdsextensionregistry download outputdir lots bids

To download specific versions:

.. code-block:: bash

   ocdsextensionregistry download outputdir bids==v1.1.4

You can mix and match specifying extensions and versions:

.. code-block:: bash

   ocdsextensionregistry download outputdir lots bids==v1.1.4

If you've already downloaded versions of extensions, you will need to specify how to handle repeated downloads using the ``--overwrite`` option:

--overwrite any         overwrite any downloaded versions
--overwrite none        overwrite no downloaded versions
--overwrite live        overwrite only live versions (like the master branch of an extension)

Within the output directory, the extension files are organized like `{extension}/{version}/{files}`, for example: ``lots/v1.1.4/README.md``.

generate-pot-files
------------------

Create POT files (message catalogs) for versions of extensions in a local directory, for example:

.. code-block:: bash

   ocdsextensionregistry generate-pot-files build/locale

You can specify versions and extensions like with the ``download`` command.

`Sphinx <http://www.sphinx-doc.org/>`__ is used to extract messages from Markdown files. To see Sphinx's standard output, use the ``--verbose`` option.

Within the output directory, the POT files are organized like `{extension}/{version}/{files}`, for example: ``lots/v1.1.4/docs.pot``.

This command can be run offline if ``--versions-dir`` is set to a local directory organized like the output directory of the ``download`` command, and if ``--extension-versions-url`` and ``--extensions-url`` are set to local files, for example:

.. code-block:: bash

   ocdsextensionregistry generate-pot-files --versions-dir outputdir --extension-versions-url file://path/to/extension_versions.csv --extensions-url file://path/to/extensions.csv build/locale

generate-data-file
------------------

Generate a data file in JSON format with all the information about versions of extensions, for example:

.. code-block:: bash

   ocdsextensionregistry generate-data-file > data.json

You can specify versions and extensions like with the ``download`` command.

To add translations to the data file, set the ``--locale-dir`` option to a directory containing MO files, for example:

.. code-block:: bash

   ocdsextensionregistry generate-data-file --locale-dir locale > data.json

The default behavior is to add all available translations, To select translations, use the ``--languages`` option, for example:

.. code-block:: bash

   ocdsextensionregistry generate-data-file --locale-dir locale --languages es > data.json

To create MO files from existing translations, see :doc:`translation`.

By default, the publisher name of an extension version is like "open-contracting-extensions". If the version is on GitHub, you can have the publisher name be like "Open Contracting Data Standard Extensions" by `generating a personal access token <https://github.com/settings/tokens/new>`__ (do not select any scopes), copying it, and setting a ``OCDS_GITHUB_ACCESS_TOKEN`` environment variable to it.

This command can be run offline if ``--versions-dir`` is set to a local directory organized like the output directory of the ``download`` command, and if ``--extension-versions-url`` and ``--extensions-url`` are set to local files, for example:

.. code-block:: bash

   ocdsextensionregistry generate-data-file --versions-dir outputdir --extension-versions-url file://path/to/extension_versions.csv --extensions-url file://path/to/extensions.csv > data.json

The data file is organized as below. To keep it short, the sample shows only one version of one extension, and only one row of one codelist, and it truncates the Markdown content of documentation files and the parsed content of schema files.

.. code-block:: json

   {
     "risk_allocation": {
       "id": "risk_allocation",
       "category": "ppp",
       "core": false,
       "name": {
         "en": "Risk Allocation"
       },
       "description": {
         "en": "Draft risk allocation extension for ppp extension"
       },
       "latest_version": "master",
       "versions": {
         "master": {
           "id": "risk_allocation",
           "date": "",
           "version": "master",
           "base_url": "https://raw.githubusercontent.com/open-contracting-extensions/ocds_riskAllocation_extension/master/",
           "download_url": "https://github.com/open-contracting-extensions/ocds_riskAllocation_extension/archive/master.zip",
           "metadata": {
             "name": {
               "en": "Risk Allocation"
             },
             "description": {
               "en": "Draft risk allocation extension for ppp extension"
             },
             "documentationUrl": {
               "en": "https://github.com/open-contracting-extensions/ocds_riskAllocation_extension"
             },
             "compatibility": [
               "1.1"
             ],
             "codelists": [
               "riskAllocation.csv",
               "riskCategory.csv"
             ],
             "schemas": [
               "release-schema.json"
             ]
           },
           "schemas": {
             "record-package-schema.json": {},
             "release-package-schema.json": {},
             "release-schema.json": {
               "en": {
                 "definitions": {
                   "Risk": "<rest of schema>"
                 }
               }
             }
           },
           "codelists": {
             "riskAllocation.csv": {
               "en": {
                 "fieldnames": [
                   "Code",
                   "Title",
                   "Description"
                 ],
                 "rows": [
                   {
                     "Code": "publicAuthority",
                     "Title": "Public authority",
                     "Description": "The risk is wholly or mostly retained by the public authority"
                   },
                   {
                     "…": "<rest of codes>"
                   }
                 ]
               }
             },
             "…": "<rest of codelists>"
           },
           "readme": {
             "en": "# Risk allocation\n\nThe [framework for disclosure in PPPs](http://pubdocs.worldbank.org/en/773541448296707678/Disclosure-in-PPPs-Framework.pdf) …"
           }
         },
         "…": "<rest of versions>"
       }
     },
     "…": "<rest of extensions>"
   }
