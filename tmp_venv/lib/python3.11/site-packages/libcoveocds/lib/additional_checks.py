from collections import defaultdict


def flatten_dict(data, path=""):
    for key, value in data.items():
        if not value:
            yield (f"{path}/{key}", value)
        elif isinstance(value, dict):
            yield from flatten_dict(value, f"{path}/{key}")
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    yield from flatten_dict(item, f"{path}/{key}/{i}")
                else:
                    yield (f"{path}/{key}/{i}", item)
        else:
            yield (f"{path}/{key}", value)


def empty_field(_data, flat):
    """Yield fields, objects and arrays that are set but empty or containing only whitespace."""
    for key, value in flat.items():
        if (isinstance(value, str) and not value.strip()) or (isinstance(value, (dict, list)) and not value):
            yield {"json_location": key}


CHECKS = {"all": [empty_field], "none": []}


def run_additional_checks(package, functions):
    if "records" in package:
        key = "records"
    elif "releases" in package:
        key = "releases"
    else:
        return {}

    releases_or_records = package[key]
    if not isinstance(releases_or_records, list):
        return {}

    results = defaultdict(list)

    for i, release_or_record in enumerate(releases_or_records):
        if not isinstance(release_or_record, dict):
            continue
        flat = dict(flatten_dict(release_or_record, f"{key}/{i}"))
        for function in functions:
            for output in function(release_or_record, flat):
                results[function.__name__].append(output)

    # https://stackoverflow.com/a/12842716/244258
    results.default_factory = None
    return results
