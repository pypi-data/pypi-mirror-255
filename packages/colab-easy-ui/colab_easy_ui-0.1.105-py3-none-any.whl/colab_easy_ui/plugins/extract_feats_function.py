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
from easy_vc_dev.utils.extract_feature import extract_feats as _extract_feats  # noqa


class ExtractFeatsWrapper:
    def __init__(self):
        self.progresses = ProgressTaskStatus(processStatus={})

    def extract_feats_function(self, port: int, uuid_str: str, project_name: str, version: int, device_id: int):
        self.port = port
        self.uuid_str = uuid_str
        try:
            _extract_feats(project_name, version, device_id, self.extract_feats_callback)
        except Exception as e:
            print("extract_feats_function exception:", e)
            open("extract_feats1eeee.txt", "w").write(e)

        self.update_status("DONE")

    def extract_feats_callback(self, data_type: str, n: int, total: int, status: str):
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


def extract_feats(port: int, project_name: str, version: int, device_id: int, background_tasks: BackgroundTasks):
    if sanitaize_path(project_name) is False:
        data = ProgressFunctionCallResponse(
            status="NG",
            uuid="",
            message=f"not valid project name {project_name}",
        )
        json_compatible_item_data = jsonable_encoder(data)
        return JSONResponse(content=json_compatible_item_data)

    # UUIDを作成
    uuid_str = str(uuid.uuid4())

    extract_feats_wrapper = ExtractFeatsWrapper()
    background_tasks.add_task(extract_feats_wrapper.extract_feats_function, port, uuid_str, project_name, version, device_id)

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
        json_compatible_item_data = jsonable_encoder(data)
        return JSONResponse(content=json_compatible_item_data)
