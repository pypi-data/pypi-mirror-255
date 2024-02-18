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
import re
from colab_easy_ui.const import sanitaize_path

sys.path.append("../easy-vc-dev")
from easy_vc_dev.train.train import train as _train  # noqa


class TrainWrapper:
    def __init__(self):
        self.progresses = ProgressTaskStatus(processStatus={})

    def train_function(
        self,
        port: int,
        uuid_str: str,
        project_name: str,
        # config_path: str,
        sample_rate: int,
        use_f0: bool,
        total_epoch: int,
        batch_size: int,
        device_id: int,
        log_step_interval: int,
        val_step_interval: int,
        test_step_interval: int,
        save_model_epoch_interval: int,
        checkpoint_path: str | None = None,
        cache_gpu: bool = False,
        freeze_vocoder: bool = False,
        finetune: bool = True,
        vocoder_ckpt: str | None = None,
    ):
        self.port = port
        self.uuid_str = uuid_str
        try:
            _train(
                project_name,
                # config_path,
                sample_rate,
                use_f0,
                total_epoch,
                batch_size,
                device_id,
                log_step_interval,
                val_step_interval,
                test_step_interval,
                save_model_epoch_interval,
                checkpoint_path,
                cache_gpu,
                freeze_vocoder,
                finetune,
                vocoder_ckpt,
                self.train_callback,
            )
        except Exception as e:
            print(e)
            open("train_exception.txt", "w").write(str(e))

        self.update_status("DONE")

    def train_callback(self, data_type: str, n: int, total: int, status: str):
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

        latest_keys = sorted(self.progresses.processStatus.keys())[-3:]
        new_array = {}
        for key in latest_keys:
            new_array[key] = self.progresses.processStatus[key]

        self.progresses.processStatus = new_array

        self.update_status("RUNNING")

    def update_status(self, status: JsonApiTaskStatus):
        data = json.dumps(asdict(self.progresses))
        requests.get(f"http://localhost:{self.port}/functions_set_task_status?task_id={self.uuid_str}&status={status}&data={data}")


def train(
    port: int,
    project_name: str,
    # config_path: str,
    sample_rate: int,
    use_f0: bool,
    total_epoch: int,
    batch_size: int,
    device_id: int,
    log_step_interval: int,
    val_step_interval: int,
    test_step_interval: int,
    save_model_epoch_interval: int,
    background_tasks: BackgroundTasks,
    # checkpoint_path: str | None = None,
    resume_from_epoch: int = 0,
    cache_gpu: bool = False,
    freeze_vocoder: bool = False,
    # finetune: bool = False,
):
    if sanitaize_path(project_name) == False:
        data = ProgressFunctionCallResponse(
            status="NG",
            uuid="",
            message=f"not valid project name {project_name}",
        )
        json_compatible_item_data = jsonable_encoder(data)
        return JSONResponse(content=json_compatible_item_data)

    # UUIDを作成
    uuid_str = str(uuid.uuid4())

    if resume_from_epoch == 0:
        print("train from pretrained.")
        checkpoint_path = "models/pretrained/easy-vc/amitaro-nof0-e0100-s010500.pt"
        finetune = True
    else:
        print(f"resume training from epoch {resume_from_epoch}.")
        data_dir = os.path.join("trainer", project_name, "logs")
        datafiles = [x for x in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, x))]

        epoch_pattern = rf"^.+-e{resume_from_epoch:04d}-.+\d+\.pt$"
        matched_files = [f for f in datafiles if re.match(epoch_pattern, f)]
        assert len(matched_files) == 1
        checkpoint_path = os.path.join(data_dir, matched_files[0])
        finetune = False

    train_wrapper = TrainWrapper()
    background_tasks.add_task(
        train_wrapper.train_function,
        port,
        uuid_str,
        project_name,
        # config_path,
        sample_rate,
        use_f0,
        total_epoch,
        batch_size,
        device_id,
        log_step_interval,
        val_step_interval,
        test_step_interval,
        save_model_epoch_interval,
        checkpoint_path,
        cache_gpu,
        freeze_vocoder,
        finetune,
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
