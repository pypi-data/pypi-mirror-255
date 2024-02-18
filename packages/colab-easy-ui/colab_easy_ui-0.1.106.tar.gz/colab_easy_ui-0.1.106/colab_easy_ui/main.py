import fire
from colab_easy_ui.ColabEasyUI import ColabEasyUI, JsonApiFunc

import functools
from colab_easy_ui.plugins.download_function.Downloader import DownloadParams
from colab_easy_ui.plugins.download_function.download_function import download
from colab_easy_ui.plugins.extract_feats_function import extract_feats
from colab_easy_ui.plugins.generate_filelist_function import generate_filelist
from colab_easy_ui.plugins.get_server_info_function import get_server_info_function
from colab_easy_ui.plugins.onnx_download_function import onnx_download

from colab_easy_ui.plugins.preprocess_function import preprocess
from colab_easy_ui.plugins.train_function import train
from colab_easy_ui.plugins.onnx_export_function import onnx_export

from colab_easy_ui.plugins.unzip_function import unzip
import logging
import os

downloadParams = [
    DownloadParams(
        display_name="whisper_tiny.pt",
        url="https://openaipublic.azureedge.net/main/whisper/models/65147644a518d12f04e32d6f3b26facc3f8dd46e5390956a9424a650c0ce22b9/tiny.pt",
        saveTo="./models/embedder/whisper_tiny.pt",
        hash="65147644a518d12f04e32d6f3b26facc3f8dd46e5390956a9424a650c0ce22b9",
    ),
    DownloadParams(
        display_name="amitaro-nof0-e0100-s010500.pt",
        url="https://huggingface.co/wok000/vcclient_model/resolve/main/easy-vc/amitaro-nof0-e0100-s010500.pt",
        saveTo="./models/pretrained/easy-vc/amitaro-nof0-e0100-s010500.pt",
        hash="b749d9dfaef1a93871a83f7e9f7d318071aafe823fc8da50a937d5eb5928983a",
    ),
]


logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("multipart").setLevel(logging.WARNING)


def run_server(
    ipython=None,
    logfile=None,
    # display=None,
    # download_func=None,
):
    c = ColabEasyUI.get_instance(ipython)
    port = c.port
    # ファイルアップローダ
    c.enable_file_uploader("upload", {"abc": "voice.zip"})

    # Tensorboardの登録
    c.enable_colab_internal_fetcher("trainer", ipython, logfile)

    # 機能登録
    c.register_functions(
        [
            # backgroundタスクのパラレル化がむずいので、一つずつ別タスクにする（TOBE IMPROVED）。
            JsonApiFunc("download_whisper", "progress", "whisper", "GET", "/download1", functools.partial(download, port=port, downloadParams=downloadParams[0:1])),
            JsonApiFunc("download_pretrain", "progress", "pretrain", "GET", "/download2", functools.partial(download, port=port, downloadParams=downloadParams[1:2])),
            JsonApiFunc("unzip", "progress", "unzip", "GET", "/unzip", functools.partial(unzip, port=port, zip_path="upload/voice.zip", extract_to="raw_data")),
            JsonApiFunc(
                "preprocess",
                "progress",
                "preprocess",
                "GET",
                "/preprocess",
                functools.partial(
                    preprocess,
                    port=port,
                    # project_name="amitaro2",
                    # wav_folder="raw_data/amitaro2",
                    # sample_rate=16000,
                    # jobs=4,
                    # valid_num=10,
                    # test_folder="raw_data/test",
                ),
            ),
            JsonApiFunc(
                "extract_feats",
                "progress",
                "extract feats",
                "GET",
                "/feats",
                functools.partial(
                    extract_feats,
                    port=port,
                    # project_name="amitaro2",
                    # version=1,
                    # device_id=0,
                ),
            ),
            JsonApiFunc(
                "generate_filelist",
                "progress",
                "generate filelist",
                "GET",
                "/filelist",
                functools.partial(
                    generate_filelist,
                    port=port,
                    # project_name="amitaro2",
                    # version=1,
                    # useF0=False,
                    # sid=0,
                ),
            ),
            JsonApiFunc(
                "start_train",
                "progress",
                "start train",
                "GET",
                "/train",
                functools.partial(
                    train,
                    port=port,
                    # project_name="amitaro2",
                    # config_path="16k_v2.json",
                    # sample_rate=16000,
                    # use_f0=False,
                    # total_epoch=5,
                    # batch_size=10,
                    # device_id=0,
                    # log_step_interval=100,
                    # val_step_interval=100,
                    # test_step_interval=100,
                    # save_model_epoch_interval=1,
                    # # checkpoint_path: str | None = None,
                    # # cache_gpu: bool = False,
                    # # freeze_vocoder: bool = True,
                    # # finetune: bool = False,
                ),
            ),
            JsonApiFunc(
                "onnx_export",
                "progress",
                "onnx export",
                "GET",
                "/onnx_export",
                functools.partial(
                    onnx_export,
                    port=port,
                ),
            ),
            # JsonApiFunc("get_dataset_id", "get", "get_dataset_name", "GET", "/get_dataset", functools.partial(get_dataset_function, dataset_folder="raw_data")),
            JsonApiFunc("get_server_info", "get", "get_server_info", "GET", "/get_server_info", functools.partial(get_server_info_function, dataset_folder="raw_data", project_folder="trainer")),
            # JsonApiFunc("onnx_download", "download", "onnx_download", "GET", "/onnx_download", functools.partial(onnx_download, display=display, download_func=download_func)),
            JsonApiFunc("onnx_download", "download", "onnx_download", "GET", "/onnx_download", functools.partial(onnx_download)),
        ]
    )

    # 静的ファイルのマウント
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)
    static_files_path = os.path.join(current_dir, "frontend/dist")
    print(static_files_path)
    c.mount_static_folder("/front2", static_files_path)
    # c.mount_static_folder("/front2", "frontend/dist")

    # サーバー起動
    port = c.start()
    print(port)
    return port


def main():
    fire.Fire(run_server)
