import json
import os
import sys
from alive_progress import alive_bar, alive_it
import requests

from arlas.cli.settings import Configuration, Resource


class RequestException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message


class Service:

    def list_collections(arlas: str) -> list[list[str]]:
        data = Service.__arlas__(arlas, "explore/_list")
        table = [["name", "index"]]
        for collection in data:
            table.append([
                collection.get("collection_name"),
                collection.get("params", {}).get("index_name"),
            ])
        return table

    def list_indices(arlas: str) -> list[list[str]]:
        data = json.loads(Service.__es__(arlas, "_cat/indices?format=json"))
        table = [["name", "status", "count", "size"]]
        for index in data:
            table.append([
                index.get("index"),
                index.get("status"),
                index.get("docs.count"),
                index.get("store.size")
            ])
        return table

    def describe_collection(arlas: str, collection: str) -> list[list[str]]:
        description = Service.__arlas__(arlas, "/".join(["explore", collection, "_describe"]))
        table = [["field name", "type"]]
        table.extend(Service.__get_fields__([], description.get("properties", {})))
        return table
    
    def describe_index(arlas: str, index: str) -> list[list[str]]:
        description = json.loads(Service.__es__(arlas, "/".join([index, "_mapping"])))
        table = [["field name", "type"]]
        table.extend(Service.__get_fields__([], description.get(index, {}).get("mappings", {}).get("properties", {})))
        return table
    
    def sample_collection(arlas: str, collection: str, pretty: bool, size: int) -> dict:
        sample = Service.__arlas__(arlas, "/".join(["explore", collection, "_search"]) + "?size={}".format(size))
        return sample

    def sample_index(arlas: str, collection: str, pretty: bool, size: int) -> dict:
        sample = json.loads(Service.__es__(arlas, "/".join([collection, "_search"]) + "?size={}".format(size)))
        return sample
    
    def create_collection(arlas: str, collection: str, model_resource: str, index: str, display_name: str, owner: str, orgs: list[str], is_public: bool, id_path: str, centroid_path: str, geometry_path: str, date_path: str):
        if model_resource:
            model = json.loads(Service.__fetch__(model_resource))
        else:
            model = {}
        if index:
            model["index_name"] = index
        if owner:
            model["organisations"] = {
                "owner": owner,
                "shared": orgs,
                "public": is_public
            }
        if id_path:
            model["id_path"] = id_path
        if centroid_path:
            model["centroid_path"] = centroid_path
        if geometry_path:
            model["geometry_path"] = geometry_path
        if date_path:
            model["timestamp_path"] = date_path
        if display_name:
            display_names = model.get("display_names", {})
            display_names["collection"] = display_name
            model["display_names"] = display_names
        print(json.dumps(model))
        Service.__arlas__(arlas, "/".join(["collections", collection]), put=json.dumps(model))

    def create_index_from_resource(arlas: str, index: str, mapping_resource: str, number_of_shards: int):
        mapping = json.loads(Service.__fetch__(mapping_resource))
        if not mapping.get("mappings"):
            print("Error: mapping {} does not contain \"mappings\" at its root.".format(mapping_resource), file=sys.stderr)
            exit(1)
        Service.create_index(arlas, index, mapping, number_of_shards)

    def create_index(arlas: str, index: str, mapping: str, number_of_shards: int = 1):
        index_doc = {"mappings": mapping.get("mappings"), "settings": {"number_of_shards": number_of_shards}}
        Service.__es__(arlas, "/".join([index]), put=json.dumps(index_doc))

    def delete_collection(arlas: str, collection: str):
        Service.__arlas__(arlas, "/".join(["collections", collection]), delete=True)

    def delete_index(arlas: str, index: str):
        Service.__es__(arlas, "/".join([index]), delete=True)

    def count_collection(arlas: str, collection: str) -> list[list[str]]:
        collections = []
        if collection:
            collections.append(collection)
        else:
            for line in Service.list_collections(arlas)[1:]:
                collections.append(line[0])
        table = [["collection name", "count"]]
        for collection in collections:
            count = Service.__arlas__(arlas, "/".join(["explore", collection, "_count"]))
            table.append([collection, count.get("totalnb", "UNKNOWN")])
        return table

    def count_hits(file_path: str) -> int:
        line_number = 0
        with open(file_path) as f:
            for line in f:
                line_number = line_number + 1
        return line_number                

    def __index_bulk__(arlas: str, index: str, bulk: []):
        data = os.linesep.join([json.dumps(line) for line in bulk]) + os.linesep
        result = json.loads(Service.__es__(arlas, "/".join([index, "_bulk"]), post=data, exit_on_failure=False, headers={"Content-Type": "application/x-ndjson"}))
        if result["errors"] is True:
            print("ERROR: " + json.dumps(result))

    def index_hits(arlas: str, index: str, file_path: str, bulk_size: int = 100, count: int = -1) -> dict[str, int]:
        line_number = 0
        line_in_bulk = 0
        bulk = []
        with open(file_path) as f:
            with alive_bar(count) as bar:
                for line in f:
                    line_number = line_number + 1
                    line_in_bulk = line_in_bulk + 1
                    bulk.append({
                        "index": {
                            "_index": index
                        }
                    })
                    bulk.append(json.loads(line))
                    if line_in_bulk == bulk_size:
                        try:
                            Service.__index_bulk__(arlas, index, bulk)
                        except RequestException as e:
                            print("Error on bulk insert between line {} and {} with code {}: {}".format(line_number, line_number - bulk_size, e.code, e.message))
                        bulk = []
                        line_in_bulk = 0
                    bar()
        if len(bulk) > 0:
            try:
                Service.__index_bulk__(arlas, index, bulk)
            except RequestException as e:
                print("Error on bulk insert between line {} and {} with code {}: {}".format(line_number, line_number - bulk_size, e.code, e.message))

    def __get_fields__(origin: list[str], properties: dict[str:dict]):
        fields = []
        for field, desc in properties.items():
            type = desc.get("type", "UNKNOWN")
            if type == "OBJECT" or type == "UNKNOWN":
                o = origin.copy()
                o.append(field)
                fields.extend(Service.__get_fields__(o, desc.get("properties", {})))
            else:
                o = origin.copy()
                o.append(field)
                fields.append([".".join(o), type])
        return fields
    
    def __arlas__(arlas: str, suffix, post=None, put=None, delete=None):
        endpoint = Configuration.settings.arlas.get(arlas)
        if endpoint is None:
            print("Error: arlas configuration ({}) not found among [{}].".format(arlas, ", ".join(Configuration.settings.arlas.keys())), file=sys.stderr)
            exit(1)
        url = "/".join([endpoint.server.location, suffix])
        if post:
            r = requests.post(url, data=post, headers=endpoint.server.headers)
        else:
            if put:
                r = requests.put(url, data=put, headers=endpoint.server.headers)
            else:
                if delete:
                    r = requests.delete(url, headers=endpoint.server.headers)
                else:
                    r = requests.get(url, headers=endpoint.server.headers)
        if r.ok:
            return r.json()
        else:
            print("Error: request failed with status {}: {}".format(str(r.status_code), r.content), file=sys.stderr)
            print("   url: {}".format(url), file=sys.stderr)
            exit(1)

    def __es__(arlas: str, suffix, post=None, put=None, delete=None, exit_on_failure: bool = True, headers: dict[str, str] = {}):
        endpoint = Configuration.settings.arlas.get(arlas)
        if endpoint is None:
            print("Error: arlas configuration ({}) not found among [{}].".format(arlas, ", ".join(Configuration.settings.arlas.keys())), file=sys.stderr)
            exit(1)
        if endpoint.elastic is None:
            print("Error: arlas configuration ({}) misses an elasticsearch configuration.".format(arlas), file=sys.stderr)
            exit(1)
        url = "/".join([endpoint.elastic.location, suffix])
        __headers = endpoint.elastic.headers
        __headers.update(headers)
        if post:
            r = requests.post(url, data=post, headers=__headers)
        else:
            if put:
                r = requests.put(url, data=put, headers=__headers)
            else:
                if delete:
                    r = requests.delete(url, headers=__headers)
                else:
                    r = requests.get(url, headers=__headers)
        if r.ok:
            return r.content
        else:
            if exit_on_failure:
                print("Error: request failed with status {}: {}".format(str(r.status_code), r.content), file=sys.stderr)
                print("   url: {}".format(url), file=sys.stderr)
                exit(1)
            else:
                raise RequestException(r.status_code, r.content)

    def __fetch__(resource: Resource):
        if os.path.exists(resource.location):
            content = None
            with open(resource.location) as f:
                content = f.read()
            return content
        r = requests.get(resource.location, headers=resource.headers)
        if r.ok:
            return r.content
        else:
            print("Error: request failed with status {}: {}".format(str(r.status_code), r.content), file=sys.stderr)
            print("   url: {}".format(resource.location), file=sys.stderr)
            exit(1)
