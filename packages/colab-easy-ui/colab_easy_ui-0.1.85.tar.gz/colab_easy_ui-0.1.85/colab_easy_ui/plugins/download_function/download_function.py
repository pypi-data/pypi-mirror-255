from fastapi import BackgroundTasks
from colab_easy_ui.Functions import ProgressFunctionCallResponse, ProgressTaskStatus, JsonApiTaskStatus
from typing import Callable
from dataclasses import asdict
from colab_easy_ui.plugins.download_function.Downloader import DownloadParams, Downloader
import requests
import functools
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import uuid


def exec_download(callback: Callable[[JsonApiTaskStatus, ProgressTaskStatus], None], downloadParams: list[DownloadParams]):
    downloader = Downloader(callback)
    for p in downloadParams:
        downloader.pushItem(p)
    downloader.download()
    callback("DONE", downloader.progresses)


def download_callback(status: JsonApiTaskStatus, allStatus: ProgressTaskStatus, port: int, uuid_str: str):
    import json

    data = json.dumps(asdict(allStatus))
    requests.get(f"http://localhost:{port}/functions_set_task_status?task_id={uuid_str}&status={status}&data={data}")


def download_function(port: int, uuid_str: str, downloadParams: list[DownloadParams]):
    download_callback_fixed = functools.partial(download_callback, port=port, uuid_str=uuid_str)
    exec_download(download_callback_fixed, downloadParams)


def download(port: int, downloadParams: list[DownloadParams], background_tasks: BackgroundTasks):
    # UUIDを作成
    uuid_str = str(uuid.uuid4())

    background_tasks.add_task(download_function, port, uuid_str, downloadParams)
    # await download_function(background_tasks, port, uuid_str, downloadParams)

    try:
        data = ProgressFunctionCallResponse(
            status="OK",
            uuid=uuid_str,
            message="",
        )
        json_compatible_item_data = jsonable_encoder(data)
        return JSONResponse(content=json_compatible_item_data)
    except Exception as e:
        data = ProgressFunctionCallResponse(
            status="NG",
            uuid="",
            message=str(e),
        )
        print(data)
        return JSONResponse(content=json_compatible_item_data)
