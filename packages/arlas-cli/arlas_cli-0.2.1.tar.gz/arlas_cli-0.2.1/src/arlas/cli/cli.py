import typer
import os
import sys

from arlas.cli.collections import collections
from arlas.cli.configurations import configurations
from arlas.cli.index import indices
from arlas.cli.variables import variables
from arlas.cli.settings import ARLAS, Configuration, Resource, Settings

app = typer.Typer(add_completion=False, no_args_is_help=True)
arlas_cli_version = "0.2.1"


@app.callback(invoke_without_command=True)
def init(
    config_file: str = typer.Option(None, help="Path to the configuration file if you do not want to use the default one: .arlas/cli/configuration.yaml."),
    version: bool = typer.Option(False, "--version", help="Print command line version")
):
    if config_file:
        variables["configuration_file"] = config_file
    if version:
        print(arlas_cli_version)
    if os.path.exists(variables["configuration_file"]):
        Configuration.init(configuration_file=variables["configuration_file"])
        if Configuration.settings.arlas and len(Configuration.settings.arlas) > 0:
            # Configuration is ok.
            ...
        else:
            print("Error : no arlas endpoint found in {}.".format(variables["configuration_file"]), file=sys.stderr)
            sys.exit(1)
    else:
        # we create a template to facilitate the creation of the configuration file
        os.makedirs(os.path.dirname(variables["configuration_file"]), exist_ok=True)
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
        Configuration.save(variables["configuration_file"])
        print("Warning : no configuration file found, we created an empty one for you ({}).".format(variables["configuration_file"]), file=sys.stderr)
        sys.exit(0)


def main():
    app.add_typer(collections, name="collections")
    app.add_typer(indices, name="indices")
    app.add_typer(configurations, name="confs")
    app()


if __name__ == "__main__":
    main()
