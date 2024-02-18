from concurrent.futures import ThreadPoolExecutor
import datetime
from typing import Dict, Generator, List, Optional
from dataclasses import dataclass, field
import requests
import os

__all__ = ["ObjectStore", "Index", "Object", "list_indexes"]

CPU_COUNT = os.cpu_count() if os.cpu_count() is not None else 6

API_BASE_URL = os.getenv("OBJECTIVE_API")
if not API_BASE_URL:
    API_BASE_URL = "https://api.objective.inc/v1/"
else:
    API_BASE_URL = API_BASE_URL.strip('"')

API_KEY = os.getenv("OBJECTIVE_API_KEY")
if not API_KEY:
    raise ValueError("Missing environment variable: OBJECTIVE_API_KEY")
else:
    API_KEY = API_KEY.strip('"')


@dataclass
class Object:
    id: Optional[str] = None
    date_created: Optional[str] = None
    date_updated: Optional[str] = None
    object: Optional[Dict] = None
    status: Optional[Dict] = None

    field_patches: List[Dict] = field(default_factory=list)
    field_deletes: List[Dict] = field(default_factory=list)

    def is_newer_than(self, date):
        if date is None or self.date_updated is None:
            return True
        else:
            return datetime.datetime.strptime(
                date, "%Y-%m-%dT%H:%M:%S.%fZ"
            ) >= datetime.datetime.strptime(self.date_updated, "%Y-%m-%dT%H:%M:%S.%fZ")

    def __getitem__(self, key):
        return self.object.get(key)

    def __setitem__(self, key, value):
        if self.object.get(key) != value:
            self.field_patches.append({key: value})
        self.object[key] = value

    def __delitem__(self, key):
        if key in self.object:
            self.field_deletes.append(key)
            del self.object[key]

    def refresh_status(self):
        self.status = objective_request("GET", f"objects/{self.id}/status")
        return self.status


def list_indexes(limit=None, cursor=None):
    data = {}
    if limit:
        data["limit"] = limit
    if cursor:
        data["cursor"] = cursor
    return [
        Index(index["id"], metadata={k: v for k, v in index.items() if k != "id"})
        for index in objective_request("GET", "indexes", data=data)["indexes"]
    ]


def objective_request(
    method: str, endpoint: str = API_BASE_URL, data=None, session=None
):
    url = API_BASE_URL + endpoint

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    MAX_RETRIES = 3
    for attempt in range(MAX_RETRIES):
        try:
            if method == "GET":
                response = (session if session else requests).get(
                    url,
                    headers=headers,
                    params=data,
                )
            else:
                response = (session if session else requests).request(
                    method, url, headers=headers, json=data
                )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt < MAX_RETRIES - 1:  # i.e. if it's not the last attempt
                continue
            else:
                raise (e)


@dataclass
class BatchOperation:
    success: List[Object]
    failures: List[Object]


class ObjectStore:
    def __init__(self):
        self.http_session = requests.Session()

    def __len__(self) -> int:
        count = self.size()
        if count and count.get("count"):
            return count["count"]
        else:
            return 0

    def size(self) -> int:
        return objective_request("GET", f"objects/count")

    def list_objects(self, limit: Optional[int] = 10) -> Generator[Object, None, None]:
        objects_returned = 0
        batch_limit = limit if (limit and limit < 512) else 512

        while True:
            list_objects_response = objective_request(
                "GET", f"objects", data={"limit": batch_limit}
            )
            cursor = list_objects_response.get("pagination", {}).get("next")

            for object in list_objects_response.get("objects", []):
                yield Object(**object)
                objects_returned += 1
                if limit and objects_returned >= limit:
                    break

            if not cursor or (limit is not None and objects_returned >= limit):
                break

    def get_objects(self) -> List[Object]:
        return self.get_objects_by_id([obj.id for obj in self.list_objects()])

    def get_objects_by_id(self, list_of_ids) -> List[Object]:
        with ThreadPoolExecutor(max_workers=CPU_COUNT * 12) as executor:
            return list(executor.map(self.get_object, list_of_ids))

    def get_object(self, object_id) -> Object:
        return Object(**objective_request("GET", f"objects/{object_id}"))

    def upsert_objects(self, objects: List[Object]) -> BatchOperation:

        def upsert_object(object):
            try:
                return self.upsert_object(object)
            except Exception as e:
                object.status = {"state": "error", "exception": e}
                return object

        with ThreadPoolExecutor(max_workers=CPU_COUNT * 12) as executor:
            success = []
            failures = []

            for obj in executor.map(upsert_object, objects):
                if obj.status.get("state") == "OK":
                    success.append(obj)
                else:
                    failures.append(obj)

            return BatchOperation(
                success=success,
                failures=failures,
            )

    def delete_objects(self, objects: List[Object]):

        def delete_object(object):
            try:
                return self.delete_object(object)
            except Exception as e:
                object.status = {"state": "error", "exception": e}
                return object

        with ThreadPoolExecutor(max_workers=CPU_COUNT * 12) as executor:
            success = []
            failures = []

            for obj in executor.map(delete_object, objects):
                if obj.status.get("state") == "OK":
                    success.append(obj)
                else:
                    failures.append(obj)

            return BatchOperation(
                success=success,
                failures=failures,
            )

    def upsert(self, object: Dict, id: Optional[str] = None):
        self.upsert_object(Object(id=id, object=object))

    def upsert_object(self, object):
        if (
            object.id
            and len(object.field_patches) > 0
            and len(object.field_deletes) == 0
        ):
            final_patch = {}
            for field_patch in object.field_patches:
                final_patch.update(field_patch)

            obj_response = objective_request(
                "PATCH",
                f"objects/{object.id}",
                data=final_patch,
                session=self.http_session,
            )
        elif object.id:
            obj_response = objective_request(
                "PUT",
                f"objects/{object.id}",
                data=object.object,
                session=self.http_session,
            )
            object.id = obj_response["id"]
        else:
            obj_response = objective_request(
                "POST", "objects", data=object.object, session=self.http_session
            )
            object.id = obj_response["id"]

        if not object.status:
            object.status = {}

        object.status["state"] = "OK"
        return object

    def delete_object(self, object):
        obj_response = objective_request("DELETE", f"objects/{object.id}")
        if not object.status:
            object.status = {}
        object.status["state"] = "OK"
        return object


@dataclass
class Index:
    index_id: str
    metadata: Optional[Dict] = None

    @staticmethod
    def preprocess_fields(fields):
        for field in list(fields.keys()):
            if field in [
                "searchable",
                "crawlable",
                "filterable",
            ] and isinstance(fields[field], list):
                fields[field] = {"allow": fields[field]}
        return fields

    @classmethod
    def from_template(self, template_name, fields, version: str = None):
        index_create = objective_request(
            "POST",
            "indexes",
            data={
                "configuration": {
                    "template": {
                        **{"name": template_name},
                        **({"version": version} if version else {}),
                    },
                    "fields": self.preprocess_fields(fields),
                }
            },
        )
        if not index_create:
            raise ValueError("Failed to create index!")
        else:
            return Index(index_create["id"])

    def update(self, new_fields):
        return objective_request("PUT", f"indexes/{self.index_id}", data=new_fields)

    def delete(self):
        return objective_request("DELETE", f"indexes/{self.index_id}")

    def status(self, status_type: Optional[str] = None):
        if status_type and status_type.lower() not in ["pending", "processing", "processed", "live", "error"]:
            raise ValueError("Invalid status type. Must be one of: pending, processing, processed, live, error.")
        obj_status = objective_request("GET", f"indexes/{self.index_id}/status{f'/{status_type.lower()}'if status_type else ''}")
        return obj_status.get("status")

    def search(self, index_name, query):
        return objective_request(
            "GET", f"indexes/{index_name}/search", data={"query": query}
        )
