import json


def context_api_transform(context):
    """
    Reformat `context` for use in an API context.

    -  Remove ``validation_errors_count``
    -  Remove ``additional_fields_count``
    -  Reformat ``additional_fields`` from a dict to a list of its values
    -  Rename ``additional_fields`` to ``all_additional_fields``
    -  Reformat ``data_only`` from a 3-value tuple to a 3-key dict
    -  Rename ``data_only`` to ``additional_fields``
    -  Reformat ``deprecated_fields`` from a dict to a list of its values, with keys added to values as ``field`` keys
    -  Reformat ``validation_errors`` from [ [ "{..}", [ {..}, ..] ], ..] to [ {..}, ..]:

       -  ``type`` (``message_type`` from the JSON text, repeated for each item in the list of dicts)
       -  ``field`` (``path_no_number`` from the JSON text, repeated for each item in the list of dicts)
       -  ``description`` (``message`` from the JSON text, repeated for each item in the list of dicts)
       -  ``path`` from the list of dicts
       -  ``value`` from the list of dicts
       -  Ignore other keys

    -  Reformat ``extensions``:

       -  Reformat ``extensions`` from a dict to a list of its values, for the keys not in ``invalid_extensions``
       -  Reformat ``invalid_extensions`` from a dict to a list of 2-value lists
    """
    context.pop("validation_errors_count")
    context.pop("additional_fields_count")

    context["deprecated_fields"] = [{"field": key, **value} for key, value in context["deprecated_fields"].items()]
    context["all_additional_fields"] = list(context.pop("additional_fields").values())

    # Don't move this above `context.pop("additional_fields")`.
    context["additional_fields"] = [
        {"path": path, "field": field, "usage_count": usage_count}
        for path, field, usage_count in context.pop("data_only")
    ]

    validation_errors = []
    for json_error, path_values in context["validation_errors"]:
        error = json.loads(json_error)
        validation_errors.extend(
            {
                "type": error["message_type"],
                "field": error["path_no_number"],
                "description": error["message"],
                "path": path_value.get("path", ""),
                "value": path_value.get("value", ""),
            }
            for path_value in path_values
        )
    context["validation_errors"] = validation_errors

    extensions = context["extensions"]
    if extensions:
        invalid_extension = extensions["invalid_extension"]
        extensions["extensions"] = [
            value for key, value in extensions["extensions"].items() if key not in invalid_extension
        ]
        extensions["invalid_extensions"] = list(map(list, invalid_extension.items()))

    # Context is edited in-place, but existing callers might expect a return value.
    return context
