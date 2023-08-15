import json
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, cast

import aiohttp
from pydantic import Field

from orcidlink.lib import exceptions
from orcidlink.lib.json_file import JSONLikeObject
from orcidlink.lib.service_clients.jsonrpc import JSONRPCError
from orcidlink.lib.type import ServiceBaseModel


def parse_workspace_ref(ref: str) -> Tuple[int, int, int]:
    wsid, objid, ver = ref.split("/")
    return int(wsid), int(objid), int(ver)


class JSONRPC11Error(ServiceBaseModel):
    code: int = Field(...)
    message: str = Field(...)
    data: Any | None = Field(default=None)


class JSONRPC11Service:
    def __init__(
        self, url: str, module: str, timeout: int, authorization: str | None = None
    ):
        self.url = url
        self.module = module
        self.timeout = timeout
        self.authorization = authorization

    async def call_func(
        self, func_name: str, params: Any
    ) -> Tuple[Optional[JSONLikeObject], Optional[JSONRPCError]]:
        call_params = []
        if params is not None:
            call_params.append(params)

        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.authorization is not None:
            headers["Authorization"] = self.authorization

        rpc_call = {
            "version": "1.1",
            "id": str(uuid.uuid4()),
            "method": f"{self.module}.{func_name}",
            "params": call_params,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url, headers=headers, json=rpc_call
                ) as response:
                    json_response = await response.json()
                    if response.status != 200:
                        return None, json_response.get("error")

                    result = json_response.get("result")
                    if result is None:
                        return None, None
                    return result[0], None

        except aiohttp.ContentTypeError as cte:
            # Raised if it is not application/json
            raise exceptions.ContentTypeError("Wrong content type", cte)
        except json.JSONDecodeError as jde:
            raise exceptions.JSONDecodeError("Error decoding JSON", jde)
        except Exception:
            raise exceptions.InternalServerError("Unexpected error")


@dataclass
class ObjectInfo:
    object_id: int
    object_name: str
    type_id: str
    save_date: str
    version: int
    saved_by: str
    workspace_id: int
    workspace_name: str
    checksum: str
    size: int
    metadata: Dict[str, str]


RawObjectInfo = Tuple[int, str, str, str, int, str, int, str, str, int, Dict[str, str]]


def object_info_to_dict(object_info: RawObjectInfo) -> ObjectInfo:
    [
        object_id,
        object_name,
        type_id,
        save_date,
        version,
        saved_by,
        workspace_id,
        workspace_name,
        checksum,
        size,
        metadata,
    ] = object_info

    return ObjectInfo(
        object_id=object_id,
        object_name=object_name,
        type_id=type_id,
        save_date=save_date,
        version=version,
        saved_by=saved_by,
        workspace_id=workspace_id,
        workspace_name=workspace_name,
        checksum=checksum,
        size=size,
        metadata=metadata,
    )


@dataclass
class WorkspaceInfo:
    workspace_id: int
    workspace_name: str
    owner: str
    modified_at: str
    max_object_id: int
    user_permission: str
    global_permission: str
    lock_status: str
    metadata: Dict[str, str]


RawWorkspaceInfo = Tuple[int, str, str, str, int, str, str, str, Dict[str, str]]


def workspace_info_to_dict(workspace_info: RawWorkspaceInfo) -> WorkspaceInfo:
    [
        workspace_id,
        workspace_name,
        owner,
        modified_at,
        max_object_id,
        user_permission,
        global_permission,
        lock_status,
        metadata,
    ] = workspace_info

    return WorkspaceInfo(
        workspace_id=workspace_id,
        workspace_name=workspace_name,
        owner=owner,
        modified_at=modified_at,
        max_object_id=max_object_id,
        user_permission=user_permission,
        global_permission=global_permission,
        lock_status=lock_status,
        metadata=metadata,
    )


class WorkspaceService(JSONRPC11Service):
    def __init__(self, url: str, timeout: int, authorization: str | None = None):
        super().__init__(
            url=url, module="Workspace", timeout=timeout, authorization=authorization
        )

    async def get_status(self) -> Any:
        result, error = await self.call_func("status", None)
        return result

    async def get_object_info(self, ref: str) -> ObjectInfo:
        result, error = await self.call_func(
            "get_object_info3",
            {"objects": [{"ref": ref}], "includeMetadata": 1, "ignoreErrors": 0},
        )
        if error is not None:
            # TODO: more specific message from errors
            raise Exception(f"Error fetching object info: {error.message}")
        elif result is not None and isinstance(result, dict):
            infos = result.get("infos")
            if isinstance(infos, list):
                object_info = infos[0]
                if isinstance(object_info, list):
                    # just trust for now:
                    return object_info_to_dict(cast(RawObjectInfo, object_info))
                else:
                    raise exceptions.ImpossibleError(
                        "Expected object info to be a list"
                    )
            else:
                raise exceptions.ImpossibleError("Expected object infos to be a list")

        else:
            raise exceptions.ImpossibleError(
                "Should not get a null object info since not ignoring errors"
            )

    async def get_workspace_info(self, workspace_id: int) -> WorkspaceInfo:
        result, error = await self.call_func("get_workspace_info", {"id": workspace_id})
        if error is not None:
            exceptions.UpstreamJSONRPCError("Error fetching workspace info", data=error)
            # upstream_jsonrpc_error(error)

        # Just trust
        # TODO: be paranoid and validate.
        return workspace_info_to_dict(cast(RawWorkspaceInfo, result))

    async def get_object(self, ref: str) -> Any:
        result, error = await self.call_func(
            "get_objects2",
            {
                "objects": [{"ref": ref}],
                "ignoreErrors": 0,
                "no_data": 0,
                "skip_external_system_updates": 0,
                "batch_external_system_updates": 0,
            },
        )
        if error is not None:
            exceptions.UpstreamJSONRPCError("Error fetching workspace info", data=error)
            # upstream_jsonrpc_error(error)

        if result is None:
            raise exceptions.ImpossibleError("Expected object data to be a list")

        data = result.get("data")
        if not isinstance(data, list):
            raise exceptions.ImpossibleError("Expected object data to be a list")

        workspace_object = cast(JSONLikeObject, data[0])

        # if not isinstance(workspace_object, dict):
        #     raise errors.ImpossibleError("Expected object data to be an object")

        # TODO: we should type the result, which may obviate the need for a cast?
        # or otherwise find a more graceful way.
        workspace_object["info"] = cast(
            JSONLikeObject,
            object_info_to_dict(cast(RawObjectInfo, workspace_object["info"])),
        )

        return workspace_object

    # TODO: not sure about this.
    async def can_access_object(self, ref: str) -> bool:
        params = {"objects": [{"ref": ref}]}
        await self.call_func("get_object_info3", params)
        return True
