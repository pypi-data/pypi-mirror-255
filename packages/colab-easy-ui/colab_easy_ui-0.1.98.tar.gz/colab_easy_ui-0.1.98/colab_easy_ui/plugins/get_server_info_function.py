from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from colab_easy_ui.Functions import GetFunctionCallResponse
import os
import json


def get_data_epochs(project_folder: str, project_name: str):
    datafiles = [x for x in os.listdir(os.path.join(project_folder, project_name, "logs")) if os.path.isfile(os.path.join(project_folder, project_name, "logs", x))]
    # epochs = [x.split("-")[2][1:] for x in datafiles if x.split("-")[2].startswith("e")]
    epochs: list[int] = []
    for file in datafiles:
        elem = file.split("-")
        if len(elem) < 3:
            continue
        if not elem[2].startswith("e"):
            continue
        epoch_str = elem[2][1:]
        if not epoch_str.isdecimal():
            continue
        epochs.append(int(epoch_str))

    epochs = sorted(set(epochs))
    return epochs


def get_generator_model_files(project_folder: str, project_name: str):
    datafiles = [x for x in os.listdir(os.path.join(project_folder, project_name, "logs")) if os.path.isfile(os.path.join(project_folder, project_name, "logs", x))]
    generator_model_files = [x for x in datafiles if x.endswith("gen.pt")]
    return generator_model_files


def get_best(project_folder: str, project_name: str):
    best_json = os.path.join(project_folder, project_name, "logs", "best.json")
    if not os.path.isfile(best_json):
        return {}

    best_data = json.loads(open(best_json, "r").read())
    return best_data


def get_server_info_function(
    dataset_folder: str,
    project_folder: str,
):
    if not os.path.isdir(dataset_folder):
        os.makedirs(dataset_folder)
    if not os.path.isdir(project_folder):
        os.makedirs(project_folder)
    datasets = [x for x in os.listdir(dataset_folder) if os.path.isdir(os.path.join(dataset_folder, x))]
    # projects = [x for x in os.listdir(project_folder) if os.path.isdir(os.path.join(project_folder, x))]
    try:
        projects = [
            {
                "name": x,
                "saved_epochs": get_data_epochs(project_folder, x),
                "best": get_best(project_folder, x),
                "generator_model_files": get_generator_model_files(project_folder, x),
            }
            for x in os.listdir(project_folder)
            if os.path.isdir(os.path.join(project_folder, x))
        ]
    except Exception as e:
        print(e)

    try:
        data = GetFunctionCallResponse(
            status="OK",
            message="",
            data={
                "datasets": datasets,
                "projects": projects,
            },
        )
        json_compatible_item_data = jsonable_encoder(data)
        return JSONResponse(content=json_compatible_item_data)
    except Exception as e:
        data = GetFunctionCallResponse(
            status="NG",
            message=str(e),
            data={},
        )
        print(data)
        return JSONResponse(content=json_compatible_item_data)
