Translation
===========

Setup
-----

:doc:`Install this package with command-line tools<cli>` and ``sphinx-intl``:

.. code-block:: bash

    pip install sphinx-intl

Create new translations
-----------------------

Generate POT files for all versions of all extensions:

.. code-block:: bash

    ocdsextensionregistry generate-pot-files build/locale

Or, generate POT files for only live versions of extensions:

.. code-block:: bash

    ocdsextensionregistry generate-pot-files --no-frozen build/locale

Or, generate POT files for the versions of extensions you want to translate, for example:

.. code-block:: bash

    ocdsextensionregistry generate-pot-files build/locale lots bids==v1.1.4

See OCP's [Software Development Handbook](https://ocp-software-handbook.readthedocs.io/en/latest/python/i18n.html) for other steps.

Update existing translations
----------------------------

Existing translations are stored in `ocds-extensions-translations <https://github.com/open-contracting/ocds-extensions-translations>`__.
