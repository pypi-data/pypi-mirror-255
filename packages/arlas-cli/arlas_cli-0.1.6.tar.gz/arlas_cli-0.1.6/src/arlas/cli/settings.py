from pydantic import BaseModel, Field
import yaml


class Resource(BaseModel):
    location: str = Field(default=None, title="file or http location")
    headers: dict[str, str] | None = Field(default=None, title="List of headers, if needed, for http(s) requests")


class ARLAS(BaseModel):
    server: Resource = Field(title="ARLAS Server")
    iam: Resource | None = Field(default=None, title="ARLAS IAM URL")
    keycloak: Resource | None = Field(default=None, title="Keycloak URL")
    elastic: Resource | None = Field(default=None, title="dictionary of name/es resources")
    allow_delete: bool | None = Field(default=False, title="Is delete command allowed for this configuration?")


class Settings(BaseModel):
    arlas: dict[str, ARLAS] = Field(default=None, title="dictionary of name/arlas configurations")
    mappings: dict[str, Resource] = Field(default=None, title="dictionary of name/mapping resources")
    models: dict[str, Resource] = Field(default=None, title="dictionary of name/model resources")


class Configuration:
    settings: Settings = None

    @staticmethod
    def save(configuration_file: str):
        with open(configuration_file, 'w') as file:
            yaml.dump(Configuration.settings.model_dump(), file)

    @staticmethod
    def init(configuration_file: str) -> Settings:
        with open(configuration_file, 'r') as file:
            data = yaml.safe_load(file)
            Configuration.settings = Settings.parse_obj(data)
