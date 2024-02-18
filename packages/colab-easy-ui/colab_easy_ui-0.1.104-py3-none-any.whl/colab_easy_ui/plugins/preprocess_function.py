import uuid
from fastapi import BackgroundTasks
import requests
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from colab_easy_ui.Functions import ProgressTaskStatus, ProgressFunctionCallResponse, JsonApiTaskStatus, ProgressTaskProcessStatus
from dataclasses import asdict
import json

import sys
from colab_easy_ui.const import sanitaize_path

sys.path.append("../easy-vc-dev")
from easy_vc_dev.utils.preprocess import preprocess as _preprocess  # noqa


class PreprocessWrapper:
    def __init__(self):
        self.progresses = ProgressTaskStatus(processStatus={})

    def preprocess_function(self, port: int, uuid_str: str, project_name: str, wav_folder: str, sample_rate: int, jobs: int, valid_num: int, test_folder: str):
        self.port = port
        self.uuid_str = uuid_str

        _preprocess(project_name, wav_folder, sample_rate, jobs, valid_num, test_folder, self.preprocess_callback)
        self.update_status("DONE")

    def preprocess_callback(self, data_type: str, n: int, total: int, status: str):
        if data_type not in self.progresses.processStatus:
            self.progresses.processStatus[data_type] = ProgressTaskProcessStatus(
                display_name=data_type,
                n=0,
                total=0,
                status="RUNNING",
                unit="",
            )
        self.progresses.processStatus[data_type].n = n
        self.progresses.processStatus[data_type].total = total
        self.progresses.processStatus[data_type].status = status

        self.update_status("RUNNING")

    def update_status(self, status: JsonApiTaskStatus):
        data = json.dumps(asdict(self.progresses))
        requests.get(f"http://localhost:{self.port}/functions_set_task_status?task_id={self.uuid_str}&status={status}&data={data}")


def preprocess(port: int, project_name: str, wav_folder: str, sample_rate: int, jobs: int, valid_num: int, test_folder: str, background_tasks: BackgroundTasks):
    if sanitaize_path(project_name) is False:
        data = ProgressFunctionCallResponse(
            status="NG",
            uuid="",
            message=f"not valid project name {project_name}",
        )
        json_compatible_item_data = jsonable_encoder(data)
        return JSONResponse(content=json_compatible_item_data)

    if sanitaize_path(wav_folder) is False:
        data = ProgressFunctionCallResponse(
            status="NG",
            uuid="",
            message=f"not valid wav folder {wav_folder}",
        )
        json_compatible_item_data = jsonable_encoder(data)
        return JSONResponse(content=json_compatible_item_data)

    # UUIDを作成
    uuid_str = str(uuid.uuid4())

    preprocess_wrapper = PreprocessWrapper()
    background_tasks.add_task(preprocess_wrapper.preprocess_function, port, uuid_str, project_name, wav_folder, sample_rate, jobs, valid_num, test_folder)

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
