import json
import typer
import os
import sys
from prettytable import PrettyTable

from arlas.cli.settings import Configuration, Resource
from arlas.cli.service import Service
from arlas.cli.variables import variables, configuration_file
from arlas.cli.model_infering import make_mapping

indices = typer.Typer()


@indices.command(help="List indices", name="list")
def list_indices():
    indices = Service.list_indices(variables["arlas"])
    tab = PrettyTable(indices[0], sortby="name", align="l")
    tab.add_rows(indices[1:])
    print(tab)


@indices.command(help="Describe an index")
def describe(index: str = typer.Argument(help="index's name")):
    indices = Service.describe_index(variables["arlas"], index)
    tab = PrettyTable(indices[0], sortby="field name", align="l")
    tab.add_rows(indices[1:])
    print(tab)


@indices.command(help="Display a sample of an index")
def sample(index: str = typer.Argument(help="index's name"), pretty: bool = typer.Option(default=True), size: int = typer.Option(default=10)):
    sample = Service.sample_index(variables["arlas"], index, pretty=pretty, size=size)
    print(json.dumps(sample["hits"].get("hits", []), indent=2 if pretty else None))


@indices.command(help="Create an index")
def create(
    index: str = typer.Argument(help="index's name"),
    mapping: str = typer.Option(help="Name of the mapping within your configuration, or URL or file path"),
    shards: int = typer.Option(default=1, help="Number of shards for the index")
):
    mapping_resource = Configuration.settings.mappings.get(mapping, None)
    if not mapping_resource:
        if os.path.exists(mapping):
            mapping_resource = Resource(location=mapping)
        else:
            print("Error: model {} not found".format(mapping), file=sys.stderr)
            exit(1)
    Service.create_index_from_resource(
        variables["arlas"],
        index=index,
        mapping_resource=mapping_resource,
        number_of_shards=shards)
    print("Index {} created on {}".format(index, variables["arlas"]))


@indices.command(help="Index data")
def data(
    index: str = typer.Argument(help="index's name"),
    files: list[str] = typer.Argument(help="List of pathes to the file conaining the data. Format: NDJSON"),
    bulk: int = typer.Option(default=100, help="Bulk size for indexing data")
):
    for file in files:
        if not os.path.exists(file):
            print("Error: file \"{}\" not found.".format(file), file=sys.stderr)
            exit(1)
        count = Service.count_hits(file_path=file)
        Service.index_hits(variables["arlas"], index=index, file_path=file, bulk_size=bulk, count=count)


@indices.command(help="Generate the mapping based on the data")
def mapping(
    file: str = typer.Argument(help="Path to the file conaining the data. Format: NDJSON"),
    nb_lines: int = typer.Option(default=2, help="Number of line to consider for generating the mapping. Avoid going over 10."),
    field_mapping: list[str] = typer.Option(default=[], help="Overide the mapping with the provided field/type. Example: fragment.location:geo_point"),
    push_on: str = typer.Option(default=None, help="Push the generated mapping for the provided index name"),
):
    if not os.path.exists(file):
        print("Error: file \"{}\" not found.".format(file), file=sys.stderr)
        exit(1)
    types = {}
    for fm in field_mapping:
        tmp = fm.split(":")
        if len(tmp) == 2:
            types[tmp[0]] = tmp[1]
        else:
            print("Error: invalid field_mapping \"{}\". The format is \"field:type\" like \"fragment.location:geo_point\"".format(fm), file=sys.stderr)
            exit(1)
    mapping = make_mapping(file=file, nb_lines=nb_lines, types=types)
    if push_on:
        Service.create_index(
            variables["arlas"],
            index=push_on,
            mapping=mapping)
        print("Index {} created on {}".format(push_on, variables["arlas"]))
    else:
        print(json.dumps(mapping, indent=2))


@indices.command(help="Delete an index")
def delete(
    index: str = typer.Argument(help="index's name")
):
    if not Configuration.settings.arlas.get(variables["arlas"]).allow_delete:
        print("Error: delete on \"{}\" is not allowed. To allow delete, change your configuration file ({}).".format(variables["arlas"], configuration_file), file=sys.stderr)
        exit(1)

    if typer.confirm("You are about to delete the index '{}' on the '{}' configuration.\n".format(index, variables["arlas"]),
                     prompt_suffix="Do you want to continue (del {} on {})?".format(index, variables["arlas"]),
                     default=False, ):
        if variables["arlas"] != "local" and variables["arlas"].find("test") < 0:
            if typer.prompt("WARNING: You are not on a test environment. To delete {} on {}, type the name of the configuration ({})".format(index, variables["arlas"], variables["arlas"])) != variables["arlas"]:
                print("Error: delete on \"{}\" cancelled.".format(variables["arlas"]), file=sys.stderr)
                exit(1)

        Service.delete_index(
            variables["arlas"],
            index=index)
        print("{} has been deleted on {}.".format(index, variables["arlas"]))
