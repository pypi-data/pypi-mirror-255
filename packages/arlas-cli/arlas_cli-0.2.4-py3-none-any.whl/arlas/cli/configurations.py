import sys
import typer
import yaml
from prettytable import PrettyTable
from arlas.cli.settings import ARLAS, AuthorizationService, Configuration, Resource
from arlas.cli.variables import variables

configurations = typer.Typer()


@configurations.command(help="List configurations", name="list")
def list_configurations():
    confs = []
    for (name, conf) in Configuration.settings.arlas.items():
        confs.append([name, conf.server.location])
    tab = PrettyTable(["name", "url"], sortby="name", align="l")
    tab.add_rows(confs[1:])
    print(tab)


@configurations.command(help="Add a configuration", name="create")
def create_configuration(
    name: str = typer.Argument(help="Name of the configuration"),
    server: str = typer.Option(help="ARLAS Server url"),
    headers: list[str] = typer.Option([], help="header (name:value)"),
    elastic: str = typer.Option(default=None, help="dictionary of name/es resources"),
    elastic_headers: list[str] = typer.Option([], help="header (name:value)"),
    allow_delete: bool = typer.Option(default=False, help="Is delete command allowed for this configuration?"),
    auth_token_url: str = typer.Option(default=None, help="Token URL of the authentication service"),
    auth_headers: list[str] = typer.Option([], help="header (name:value)"),
    auth_login: str = typer.Option(default=None, help="login"),
    auth_password: str = typer.Option(default=None, help="password"),
    auth_client_id: str = typer.Option(default=None, help="Client ID"),
    auth_client_secret: str = typer.Option(default=None, help="Client secret"),
    auth_grant_type: str = typer.Option(default=None, help="Grant type (e.g. password)"),
    auth_arlas_iam: bool = typer.Option(default=True, help="Is it an ARLAS IAM service?")
):
    if Configuration.settings.arlas.get(name):
        print("Error: a configuration with that name already exists, please remove it first.", file=sys.stderr)
        exit(1)

    conf = ARLAS(
        server=Resource(location=server, headers=dict(map(lambda h: (h.split(":")[0], h.split(":")[1]), headers))),
        allow_delete=allow_delete)
    if auth_token_url:
        conf.authorization = AuthorizationService(
            token_url=Resource(location=auth_token_url, headers=dict(map(lambda h: (h.split(":")[0], h.split(":")[1]), auth_headers))),
            login=auth_login,
            password=auth_password,
            client_id=auth_client_id,
            client_secret=auth_client_secret,
            grant_type=auth_grant_type,
            arlas_iam=auth_arlas_iam
        )
    if elastic:
        conf.elastic = Resource(location=elastic, headers=dict(map(lambda h: (h.split(":")[0], h.split(":")[1]), elastic_headers)))
    Configuration.settings.arlas[name] = conf
    Configuration.save(variables["configuration_file"])
    Configuration.init(variables["configuration_file"])
    print("Configuration {} created.".format(name))


@configurations.command(help="Delete a configuration", name="delete")
def delete_configuration(
    name: str = typer.Argument(help="Name of the configuration"),
):
    if Configuration.settings.arlas.get(name) is None:
        print("Error: no configuration found for {}.".format(name), file=sys.stderr)
        exit(1)
    Configuration.settings.arlas.pop(name)
    Configuration.save(variables["configuration_file"])
    Configuration.init(variables["configuration_file"])
    print("Configuration {} deleted.".format(name))


@configurations.command(help="Describe a configuration", name="describe")
def describe_configuration(
    name: str = typer.Argument(help="Name of the configuration"),
):
    if Configuration.settings.arlas.get(name) is None:
        print("Error: no configuration found for {}.".format(name), file=sys.stderr)
        exit(1)
    print(yaml.dump(Configuration.settings.arlas[name].model_dump()))