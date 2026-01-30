import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import click

import libcoveocds.api
from libcoveocds.config import LibCoveOCDSConfig
from libcoveocds.lib.additional_checks import CHECKS


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


@click.command()
@click.argument("filename")
@click.option(
    "-s",
    "--schema-version",
    type=click.Choice(LibCoveOCDSConfig().config["schema_version_choices"]),
    help="Version of the schema to validate the data, eg '1.0'",
)
@click.option("-c", "--convert", is_flag=True, help="Convert FILENAME to CSV, ODS and Excel files")
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(path_type=Path),
    help="Output directory (defaults to basename of FILENAME)",
)
@click.option("-d", "--delete", is_flag=True, help="Delete output directory if it exists")
@click.option("-e", "--exclude-file", is_flag=True, help="Exclude FILENAME from the output directory")
@click.option(
    "--additional-checks", default="all", type=click.Choice(CHECKS), help="The set of additional checks to perform"
)
@click.option("--skip-aggregates", is_flag=True, help="Skip releases_aggregates and records_aggregates")
@click.option(
    "--standard-zip",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to a ZIP file containing the standard repository",
)
def main(
    filename,
    output_dir,
    convert,
    schema_version,
    delete,
    exclude_file,
    additional_checks,
    skip_aggregates,
    standard_zip,
):
    if standard_zip:
        standard_zip = f"file://{standard_zip}"

    config = LibCoveOCDSConfig()
    config.config["standard_zip"] = standard_zip
    config.config["additional_checks"] = additional_checks
    config.config["skip_aggregates"] = skip_aggregates
    config.config["context"] = "api"

    keep_files = convert or output_dir
    if keep_files:
        if not output_dir:
            output_dir = Path(Path(filename).stem)

        if output_dir.exists():
            if delete:
                shutil.rmtree(output_dir)
            else:
                sys.exit(f"Directory {output_dir} already exists")
        output_dir.mkdir(parents=True)

        if not exclude_file:
            shutil.copy2(filename, output_dir)
    else:
        output_dir = tempfile.mkdtemp(prefix="lib-cove-ocds-cli-", dir=tempfile.gettempdir())

    try:
        result = libcoveocds.api.ocds_json_output(
            output_dir, filename, schema_version, convert=convert, lib_cove_ocds_config=config
        )
    finally:
        if not keep_files:
            shutil.rmtree(output_dir)

    output = json.dumps(result, indent=2, cls=SetEncoder)
    if keep_files:
        with open(os.path.join(output_dir, "results.json"), "w") as f:
            f.write(output)
    click.echo(output)


if __name__ == "__main__":
    main()
