Contributing
============

Methods in this library should either apply to all possible extensions, or be useful to at least two use cases. Methods that don't yet meet these criteria are documented as experimental.

ProfileBuilder warns instead of errors about bad extensions. Specifically, it warns about issues retrieving an extension's ``release-schema.json`` file and codelists files. If a new error is raised, edit the code in:

-  :meth:`ocdsextensionregistry.profile_builder.ProfileBuilder.release_schema_patch`
-  :attr:`ocdsextensionregistry.extension_version.ExtensionVersion.codelists`
