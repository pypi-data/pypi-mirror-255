import json
import typer
import os
import sys
from prettytable import PrettyTable

from arlas.cli.settings import Configuration, Resource
from arlas.cli.service import Service
from arlas.cli.variables import variables

collections = typer.Typer()


@collections.command(help="List collections", name="list")
def list_collections():
    collections = Service.list_collections(variables["arlas"])
    tab = PrettyTable(collections[0], sortby="name", align="l")
    tab.add_rows(collections[1:])
    print(tab)


@collections.command(help="Count the number of hits within a collection (or all collection if not provided)")
def count(collection: str = typer.Argument(default=None, help="Collection's name")):
    count = Service.count_collection(variables["arlas"], collection)
    tab = PrettyTable(count[0], sortby="collection name", align="l")
    tab.add_rows(count[1:])
    print(tab)


@collections.command(help="Describe a collection")
def describe(collection: str = typer.Argument(help="Collection's name")):
    collections = Service.describe_collection(variables["arlas"], collection)
    tab = PrettyTable(collections[0], sortby="field name", align="l")
    tab.add_rows(collections[1:])
    print(tab)


@collections.command(help="Display a sample of a collection")
def sample(collection: str = typer.Argument(help="Collection's name"), pretty: bool = typer.Option(default=True), size: int = typer.Option(default=10)):
    sample = Service.sample_collection(variables["arlas"], collection, pretty=pretty, size=size)
    print(json.dumps(sample.get("hits", []), indent=2 if pretty else None))


@collections.command(help="Delete a collection")
def delete(
    collection: str = typer.Argument(help="collection's name")
):
    if typer.confirm("You are about to delete the collection '{}' on the '{}' configuration.\n".format(collection, variables["arlas"]),
                     prompt_suffix="Do you want to continue (del {} on {})?".format(collection, variables["arlas"]),
                     default=False, ):
        Service.delete_collection(
            variables["arlas"],
            collection=collection)
        print("{} has been deleted on {}.".format(collection, variables["arlas"]))


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
        variables["arlas"],
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
    print("Collection {} created on {}".format(collection, variables["arlas"]))

