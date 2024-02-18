from fastapi import APIRouter
from typing import Callable, Dict, Any, TypeAlias, Literal
from dataclasses import dataclass


from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from colab_easy_ui.data.Response import ColabEasyUIResponse


JsonApiFuncType: TypeAlias = Literal[
    "oneshot",
    "progress",
    "get",
    "download",
]

JsonApiTaskStatus: TypeAlias = Literal[
    "RUNNING",
    "DONE",
    "NOT_FOUND",
]

JsonApiTaskProcessStatus: TypeAlias = Literal[
    "RUNNING",
    "VALIDATING",
    "DONE",
    "ERROR_INVALID_CHECKSUM",
    "ERROR_DOWNLOAD_NOT_FOUND",
]


@dataclass
class JsonApiFuncInfo:
    """
    JsonAPIの情報。情報を取得するときに使用する。
    """

    id: str
    type: JsonApiFuncType
    display_name: str
    method: str
    path: str


@dataclass
class JsonApiFunc(JsonApiFuncInfo):
    """
    JsonAPIの情報。情報を登録するときに使用する。呼びさす関数をメンバーに持つ。
    """

    func: Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass
class FunctionInfoResponse(ColabEasyUIResponse):
    """
    JsonAPIの情報取得APIのレスポンス
    """

    functions: list[JsonApiFuncInfo]


@dataclass
class FunctionTaskStatus:
    """
    JsonAPIのタスク情報
    """

    status: JsonApiTaskStatus
    data: Any


@dataclass
class GetFunctionTaskStatusResponse(ColabEasyUIResponse):
    """
    JsonAPIのタスク情報取得APIのレスポンス
    """

    task_id: str
    task_status: JsonApiTaskStatus
    task_status_data: str  # jsonの文字列。setの時にhttp経由で文字列で来るのでDict方にしていない。


@dataclass
class ProgressFunctionCallResponse(ColabEasyUIResponse):
    """
    progress型のJsonAPIコール時のレスポンス。uuidが返るのでこれで進捗等のステータスを確認する。
    """

    uuid: str


@dataclass
class GetFunctionCallResponse(ColabEasyUIResponse):
    """
    get型のJsonAPIコール時のレスポンス。
    """

    data: Dict[str, Any]


@dataclass
class ProgressTaskProcessStatus:
    """
    非同期API内の処理の進捗を管理するクラス
    """

    display_name: str
    n: int
    total: int
    status: JsonApiTaskProcessStatus
    unit: str


# AllProgressTaskProcessStatus: TypeAlias = Dict[str, ProgressTaskProcessStatus]
@dataclass
class ProgressTaskStatus:
    processStatus: Dict[str, ProgressTaskProcessStatus]


class Functions:
    def __init__(self):
        self.status_store: Dict[str, FunctionTaskStatus] = {}

    def register_functions(self, funcs: list[JsonApiFunc]):
        self.functions = funcs

        router = APIRouter()
        for func in funcs:
            router.add_api_route(func.path, func.func, methods=[func.method])
        router.add_api_route("/functions", self.get_function_info, methods=["GET"])
        router.add_api_route("/functions_set_task_status", self.set_task_status, methods=["GET"])
        router.add_api_route("/functions_del_task_status", self.del_task_status, methods=["GET"])
        router.add_api_route("/functions_get_task_status", self.get_task_status, methods=["GET"])

        self.router = router

    def set_task_status(self, task_id: str, status: JsonApiTaskStatus, data: str):
        self.status_store[task_id] = FunctionTaskStatus(status, data)
        # print(self.status_store)

    def del_task_status(self, task_id: str):
        del self.status_store[task_id]

    def get_task_status(self, task_id: str):
        if task_id not in self.status_store:
            data = GetFunctionTaskStatusResponse(
                status="OK",
                message="",
                task_id=task_id,
                task_status="NOT_FOUND",
                task_status_data="",
            )
            json_compatible_item_data = jsonable_encoder(data)
            return JSONResponse(content=json_compatible_item_data)

        data = GetFunctionTaskStatusResponse(
            status="OK",
            message="",
            task_id=task_id,
            task_status=self.status_store[task_id].status,
            task_status_data=self.status_store[task_id].data,
        )
        json_compatible_item_data = jsonable_encoder(data)
        return JSONResponse(content=json_compatible_item_data)

    def get_function_info(self):
        if self.functions is None:
            data = ColabEasyUIResponse(
                status="error",
                message="No functions registered.",
            )
            return JSONResponse(content=jsonable_encoder(data))

        functions: list[JsonApiFuncInfo] = []
        for f in self.functions:
            f_info = JsonApiFuncInfo(
                id=f.id,
                type=f.type,
                display_name=f.display_name,
                method=f.method,
                path=f.path,
            )
            functions.append(f_info)

        data = FunctionInfoResponse(
            status="ok",
            message="",
            functions=functions,
        )

        json_compatible_item_data = jsonable_encoder(data)
        return JSONResponse(content=json_compatible_item_data)
