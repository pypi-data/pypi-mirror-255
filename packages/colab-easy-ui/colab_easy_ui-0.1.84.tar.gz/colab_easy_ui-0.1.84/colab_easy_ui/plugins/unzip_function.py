import zipfile
import os
from typing import Callable
import uuid
from fastapi import BackgroundTasks
import requests
import functools
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from colab_easy_ui.Functions import ProgressTaskStatus, ProgressFunctionCallResponse, JsonApiTaskStatus, ProgressTaskProcessStatus
from dataclasses import asdict


def exec_unzip(_callback: Callable[[JsonApiTaskStatus, ProgressTaskStatus], None], zip_path: str, extract_to: str):
    progresses = ProgressTaskStatus(processStatus={})

    os.makedirs(extract_to, exist_ok=True)
    progresses.processStatus["unzip"] = ProgressTaskProcessStatus(
        display_name="Unzip",
        n=0,
        total=0,
        status="RUNNING",
        unit="",
    )

    # ZIPファイルを開く
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        # 解凍するファイルリストを取得
        file_list = zip_ref.namelist()
        # ファイルの総数を取得し、進捗バーの最大値として設定
        total_files = len(file_list)
        # tqdmを使用して進捗表示を行う
        for i, file in enumerate(file_list):
            # ファイルを解凍
            zip_ref.extract(file, extract_to)
            progresses.processStatus["unzip"].n = i
            progresses.processStatus["unzip"].total = total_files
            progresses.processStatus["unzip"].status = "RUNNING"
            _callback("RUNNING", progresses)

        progresses.processStatus["unzip"].status = "DONE"
        _callback("DONE", progresses)


def unzip_callback(status: JsonApiTaskStatus, allStatus: ProgressTaskStatus, port: int, uuid_str: str):
    import json

    data = json.dumps(asdict(allStatus))
    requests.get(f"http://localhost:{port}/functions_set_task_status?task_id={uuid_str}&status={status}&data={data}")


def unzip_function(port: int, uuid_str: str, zip_path: str, extract_to: str):
    unzip_callback_fixed = functools.partial(unzip_callback, port=port, uuid_str=uuid_str)
    exec_unzip(unzip_callback_fixed, zip_path, extract_to)


def unzip(port: int, zip_path: str, extract_to: str, background_tasks: BackgroundTasks):
    # UUIDを作成
    uuid_str = str(uuid.uuid4())

    background_tasks.add_task(unzip_function, port, uuid_str, zip_path, extract_to)

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
