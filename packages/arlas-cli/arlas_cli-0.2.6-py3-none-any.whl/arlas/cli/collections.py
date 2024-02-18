import json
import typer
import os
import sys
from prettytable import PrettyTable

from arlas.cli.settings import Configuration, Resource
from arlas.cli.service import Service
from arlas.cli.variables import variables

collections = typer.Typer()


@collections.callback()
def configuration(config: str = typer.Option(help="Name of the ARLAS configuration to use from your configuration file ({}).".format(variables["configuration_file"]))):
    variables["arlas"] = config


@collections.command(help="List collections", name="list")
def list_collections():
    config = variables["arlas"]
    collections = Service.list_collections(config)
    tab = PrettyTable(collections[0], sortby="name", align="l")
    tab.add_rows(collections[1:])
    print(tab)


@collections.command(help="Count the number of hits within a collection (or all collection if not provided)")
def count(
    collection: str = typer.Argument(default=None, help="Collection's name")
):
    config = variables["arlas"]
    count = Service.count_collection(config, collection)
    tab = PrettyTable(count[0], sortby="collection name", align="l")
    tab.add_rows(count[1:])
    print(tab)


@collections.command(help="Describe a collection")
def describe(
    collection: str = typer.Argument(help="Collection's name")
):
    config = variables["arlas"]
    fields = Service.describe_collection(config, collection)
    tab = PrettyTable(fields[0], sortby="field name", align="l")
    tab.add_rows(fields[1:])
    print(tab)

    fields = Service.metadata_collection(config, collection)
    tab = PrettyTable(fields[0], align="l")
    tab.add_rows(fields[1:])
    print(tab)


@collections.command(help="Display a sample of a collection")
def sample(
    collection: str = typer.Argument(help="Collection's name"),
    pretty: bool = typer.Option(default=True),
    size: int = typer.Option(default=10)
):
    config = variables["arlas"]
    sample = Service.sample_collection(config, collection, pretty=pretty, size=size)
    print(json.dumps(sample.get("hits", []), indent=2 if pretty else None))


@collections.command(help="Delete a collection")
def delete(
    collection: str = typer.Argument(help="collection's name")
):
    config = variables["arlas"]
    if typer.confirm("You are about to delete the collection '{}' on the '{}' configuration.\n".format(collection, config),
                     prompt_suffix="Do you want to continue (del {} on {})?".format(collection, config),
                     default=False, ):
        Service.delete_collection(
            config,
            collection=collection)
        print("{} has been deleted on {}.".format(collection, config))


@collections.command(help="Create a collection")
def create(
    collection: str = typer.Argument(help="Collection's name"),
    model: str = typer.Option(default=None, help="Name of the model within your configuration, or URL or file path"),
    index: str = typer.Option(default=None, help="Name of the index referenced by the collection"),
    display_name: str = typer.Option(default=None, help="Display name of the collection"),
    public: bool = typer.Option(default=False, help="Whether the collection is public or not"),
    owner: str = typer.Option(default=None, help="Organisation's owner"),
    orgs: list[str] = typer.Option(default=[], help="List of organisations accessing the collection"),
    id_path: str = typer.Option(default=None, help="Overide the JSON path to the id field."),
    centroid_path: str = typer.Option(default=None, help="Overide the JSON path to the centroid field."),
    geometry_path: str = typer.Option(default=None, help="Overide the JSON path to the geometry field."),
    date_path: str = typer.Option(default=None, help="Overide the JSON path to the date field.")
):
    config = variables["arlas"]
    if not owner and (orgs or public):
        print("Error: an owner must be provided for sharing the collection.", file=sys.stderr)
        exit(1)
    model_resource = None
    if model:
        model_resource = Configuration.settings.models.get(model, None)
        if not model_resource:
            if os.path.exists(model):
                model_resource = Resource(location=model)
            else:
                print("Error: model {} not found".format(model), file=sys.stderr)
                exit(1)
    Service.create_collection(
        config,
        collection,
        model_resource=model_resource,
        index=index,
        display_name=display_name,
        owner=owner,
        orgs=orgs,
        is_public=public,
        id_path=id_path,
        centroid_path=centroid_path,
        geometry_path=geometry_path,
        date_path=date_path)
    print("Collection {} created on {}".format(collection, config))
