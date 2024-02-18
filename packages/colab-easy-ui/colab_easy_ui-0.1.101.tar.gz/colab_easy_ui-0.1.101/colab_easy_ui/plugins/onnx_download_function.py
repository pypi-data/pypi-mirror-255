from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from colab_easy_ui.Functions import ProgressFunctionCallResponse
import os
import sys
from fastapi.responses import FileResponse
from colab_easy_ui.const import is_running_on_colab, sanitaize_path

sys.path.append("../easy-vc-dev")
from easy_vc_dev.onnx.export_onnx import export_onnx as _export_onnx  # noqa


def onnx_download(
    project_name: str,
    torch_file: str,
    # ipython=None,
    # display=None,
    # download_func=None,
):
    # open("onnx_download1.txt", "w").write("Eonnx_download")

    # if is_running_on_colab() is True:
    #     # open("onnx_download2-1.txt", "w").write(display)
    #     open("onnx_download2-2.txt", "w").write("ERonnx_download")
    #     try:
    #         # display.download("/content/sample_data/mnist_train_small.csv")
    #         display(download_func("/content/sample_data/mnist_train_small.csv"))
    #     except Exception as e:
    #         open("onnx_download2-2-2.txt", "w").write(str(e))
    #     open("onnx_download3.txt", "w").write("ERonnx_download")
    #     # from google.colab import files

    #     # files.download("/content/sample_data/mnist_train_small.csv")

    # return

    if sanitaize_path(project_name) is False or sanitaize_path(torch_file) is False:
        data = ProgressFunctionCallResponse(
            status="NG",
            uuid="",
            message=f"not valid project name {project_name} or torch_file {torch_file}",
        )
        json_compatible_item_data = jsonable_encoder(data)
        return JSONResponse(content=json_compatible_item_data)

    file_path = os.path.join("trainer", project_name, "logs", os.path.splitext(torch_file)[0] + ".onnx")

    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    file_size = os.path.getsize(file_path)
    headers = {
        "Content-Length": str(file_size),
    }

    return FileResponse(path=file_path, filename=os.path.basename(file_path), media_type="application/octet-stream", headers=headers)
