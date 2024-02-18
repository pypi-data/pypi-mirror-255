import typer
import os
import sys

from arlas.cli.collections import collections
from arlas.cli.index import indices
from arlas.cli.variables import variables, configuration_file
from arlas.cli.settings import ARLAS, Configuration, Resource, Settings

app = typer.Typer(add_completion=False)
arlas_cli_version = "0.1.16"


@app.callback()
def collections_callback(
    config: str = typer.Option(help="Name of the ARLAS configuration to use from your configuration file ({}).".format(configuration_file))
):
    variables["arlas"] = config


def main():
    if os.path.exists(configuration_file):
        Configuration.init(configuration_file=configuration_file)
        if Configuration.settings.arlas and len(Configuration.settings.arlas) > 0:
            # Configuration is ok.
            ...
        else:
            print("Error : no arlas endpoint found in {}.".format(configuration_file), file=sys.stderr)
            sys.exit(1)
    else:
        # we create a template to facilitate the creation of the configuration file
        print(os.path.dirname(configuration_file))
        os.makedirs(os.path.dirname(configuration_file), exist_ok=True)
        Configuration.settings = Settings(
            arlas={
                "demo": ARLAS(server=Resource(location="https://demo.cloud.arlas.io/arlas/server", headers={"Content-Type": "application/json"})),
                "local": ARLAS(
                    server=Resource(location="http://localhost:9999/arlas", headers={"Content-Type": "application/json"}),
                    elastic=Resource(location="http://localhost:9200", headers={"Content-Type": "application/json"}),
                    allow_delete=True
                )
            },
            mappings={
                "arlas_eo": Resource(location="https://raw.githubusercontent.com/gisaia/ARLAS-EO/master/mapping.json")
            },
            models={
                "arlas_eo": Resource(location="https://raw.githubusercontent.com/gisaia/ARLAS-EO/master/collection.json")
            }
        )
        Configuration.save(configuration_file)
        print("Warning : no configuration file found, we created an empty one for you ({}).".format(configuration_file), file=sys.stderr)
        sys.exit(0)
    app.add_typer(collections, name="collections")
    app.add_typer(indices, name="indices")
    app()


if __name__ == "__main__":
    main()
