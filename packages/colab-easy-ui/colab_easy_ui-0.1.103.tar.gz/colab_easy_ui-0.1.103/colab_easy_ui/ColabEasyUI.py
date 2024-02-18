import os
from typing import Callable
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from fastapi.routing import APIRoute
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from colab_easy_ui.EasyFileUploaderInternal import EasyFileUploader
import uvicorn
import threading
import nest_asyncio
import portpicker
from colab_easy_ui.ColabInternalFetcher import ColabInternalFetcher
from colab_easy_ui.Functions import Functions, JsonApiFunc


class ValidationErrorLoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        open("ERROR_LOGGING1.txt", "w").write("ERRORLOGGING")

        async def custom_route_handler(request: Request) -> Response:
            try:
                open("ERROR_LOGGING2.txt", "w").write("ERRORLOGGING")
                return await original_route_handler(request)
            except RequestValidationError as exc:  # type: ignore
                open("ERROR_LOGGING3.txt", "w").write(str(e))
                print("Exception", request.url, str(exc))
                body = await request.body()
                detail = {"errors": exc.errors(), "body": body.decode()}
                raise HTTPException(status_code=422, detail=detail)

        return custom_route_handler


class ColabEasyUI(FastAPI):
    _instance = None
    port = 0

    @classmethod
    def get_instance(
        cls,
        ipython=None,
    ):
        if cls._instance is None:
            app_fastapi = ColabEasyUI(ipython)
            cls._instance = app_fastapi
            return cls._instance

        return cls._instance

    def __init__(self, ipython=None):
        super().__init__()
        self.port = portpicker.pick_unused_port()

        # self.mount(
        #     "/front",
        #     StaticFiles(directory=f"{os.path.dirname(__file__)}/front/dist", html=True),
        #     name="static",
        # )

        self.router.route_class = ValidationErrorLoggingRoute
        self.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.ipython = ipython

    def _run_server(self, port: int):
        uvicorn.run(
            self,
            host="127.0.0.1",
            port=port,
            log_level="critical",
            # log_level="info",
        )

    def start(self):
        nest_asyncio.apply()
        server_thread = threading.Thread(target=self._run_server, args=(self.port,))
        server_thread.start()
        return self.port

    def mount_static_folder(self, path: str, real_path: str):
        self.mount(
            path,
            StaticFiles(directory=real_path, html=True),
            name="static",
        )

    def enable_file_uploader(self, upload_dir: str, allowed_files: dict[str, str] | None = None):
        self.fileUploader = EasyFileUploader(upload_dir)
        self.fileUploader.set_allowed_filenames(allowed_files)
        self.include_router(self.fileUploader.router)

    def enable_colab_internal_fetcher(
        self,
        project_dir: str,
        ipython=None,
        logfile=None,
    ):
        from fastapi import APIRouter

        self.colabInternalFetcher = ColabInternalFetcher("trainer", ipython, logfile)

        router = APIRouter()
        router.add_api_route("/internal_start_tb", self.colabInternalFetcher.start_tensorboard, methods=["GET"])
        router.add_api_route("/internal_runs", self.colabInternalFetcher.get_runs, methods=["GET"])
        router.add_api_route("/internal_scalars_tags", self.colabInternalFetcher.get_scalars_tags, methods=["GET"])
        router.add_api_route("/internal_scalars_scalars", self.colabInternalFetcher.get_scalars_scalars, methods=["GET"])
        router.add_api_route("/internal_scalars_multirun", self.colabInternalFetcher.get_scalars_scalars, methods=["GET"])
        router.add_api_route("/internal_images_tags", self.colabInternalFetcher.get_images_tags, methods=["GET"])
        router.add_api_route("/internal_images_images", self.colabInternalFetcher.get_images_images, methods=["GET"])
        router.add_api_route("/internal_images_individualImage", self.colabInternalFetcher.get_images_individualImage, methods=["GET"])
        router.add_api_route("/internal_audio_tags", self.colabInternalFetcher.get_audio_tags, methods=["GET"])
        router.add_api_route("/internal_audio_audio", self.colabInternalFetcher.get_audio_audio, methods=["GET"])
        router.add_api_route("/internal_audio_individualAudio", self.colabInternalFetcher.get_audio_individualAudio, methods=["GET"])
        self.include_router(router)

    def register_functions(self, funcs: list[JsonApiFunc]):
        functions = Functions()
        functions.register_functions(funcs)
        self.include_router(functions.router)
