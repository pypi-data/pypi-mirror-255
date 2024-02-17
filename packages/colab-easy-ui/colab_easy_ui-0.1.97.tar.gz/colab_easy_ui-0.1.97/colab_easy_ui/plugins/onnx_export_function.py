import uuid
from fastapi import BackgroundTasks
import requests
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from colab_easy_ui.Functions import ProgressTaskStatus, ProgressFunctionCallResponse, JsonApiTaskStatus, ProgressTaskProcessStatus
from dataclasses import asdict
import json
import os
import sys

sys.path.append("../easy-vc-dev")
from easy_vc_dev.onnx.export_onnx import export_onnx as _export_onnx  # noqa


class OnnxExportWrapper:
    def __init__(self):
        self.progresses = ProgressTaskStatus(processStatus={})

    def onnx_export_function(
        self,
        port: int,
        uuid_str: str,
        torch_path: str,
        output_path: str,
        static_size: int = 0,
    ):
        self.port = port
        self.uuid_str = uuid_str

        try:
            _export_onnx(
                torch_path,
                output_path,
                static_size,
                self.export_callback,
            )
        except Exception as e:
            print(e)

        self.update_status("DONE")

    def export_callback(self, data_type: str, n: int, total: int, status: str):
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


def onnx_export(
    port: int,
    project_name: str,
    torch_file: str,
    background_tasks: BackgroundTasks,
    static_size: int = 0,
):
    # UUIDを作成
    uuid_str = str(uuid.uuid4())
    torch_path = os.path.join("trainer", project_name, "logs", torch_file)
    output_path = os.path.join("trainer", project_name, "logs", os.path.splitext(torch_file)[0] + ".onnx")

    onnx_export_wrapper = OnnxExportWrapper()

    background_tasks.add_task(
        onnx_export_wrapper.onnx_export_function,
        port,
        uuid_str,
        torch_path,
        output_path,
        static_size,
    )

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
