import portpicker
from fastapi.responses import Response
import requests
from tensorboard import notebook

from colab_easy_ui.const import is_running_on_colab
import os


class ColabInternalFetcher:
    tb_port = 0

    def __init__(self, project_dir: str, ipython=None, logfile=None) -> None:
        self.project_dir = project_dir
        self.ipython = ipython
        self.logfile = logfile

    def start_tensorboard_colab(self, tb_logs_dir):
        self.tb_port = portpicker.pick_unused_port()
        if self.logfile is not None:
            self.ipython.system_raw(f"tensorboard --port {self.tb_port} --logdir {tb_logs_dir}  --samples_per_plugin images=100,audio=100 >{self.logfile} 2>&1 &")
        else:
            try:
                self.ipython.system_raw(f"tensorboard --port {self.tb_port} --logdir {tb_logs_dir}  --samples_per_plugin images=100,audio=100  &")
            except Exception as e:
                print(e)
        return self.tb_port

    def start_tensorboard_normal(self, tb_logs_dir):
        self.tb_port = portpicker.pick_unused_port()
        notebook.start(f"--port {self.tb_port} --logdir {tb_logs_dir} --samples_per_plugin images=100,audio=100")
        self.tb_port = self.tb_port
        return self.tb_port

    def start_tensorboard(self, project_name: str):
        tb_logs_dir = os.path.join(self.project_dir, project_name, "logs")
        os.makedirs(tb_logs_dir, exist_ok=True)

        if is_running_on_colab() is True:
            tb_port = self.start_tensorboard_colab(tb_logs_dir)
        else:
            tb_port = self.start_tensorboard_normal(tb_logs_dir)
        print("tensorboard port:", tb_port, "logs dir:", tb_logs_dir)

    def _fetch(self, url):
        try:
            response = requests.get(url)
            content_type = response.headers.get("Content-Type")
            return Response(content=response.content, media_type=content_type)
        except Exception as e:
            print("internal fetcher exception:", e)
            return {}

    def _post(self, url, data):
        try:
            response = requests.post(url, data=data)
            content_type = response.headers.get("Content-Type")
            return Response(content=response.content, media_type=content_type)
        except Exception as e:
            print("internal fetcher exception:", e)
            return {}

    def get_runs(self):
        if self.tb_port == 0:
            return {}
        url = f"http://localhost:{self.tb_port}/data/runs"
        return self._fetch(url)

    def get_scalars_tags(self):
        if self.tb_port == 0:
            return {}
        url = f"http://localhost:{self.tb_port}/data/plugin/scalars/tags"
        return self._fetch(url)

    def get_scalars_scalars(self, run: str, tag: str):
        if self.tb_port == 0:
            return []
        url = f"http://localhost:{self.tb_port}/data/plugin/scalars/scalars?run={run}&tag={tag}"
        return self._fetch(url)

    def get_scalars_scalars_multirun(self, run: str, tag: str):
        if self.tb_port == 0:
            return []
        url = f"http://localhost:{self.tb_port}/data/plugin/scalars/scalars_multirun"

        data = {
            "tag": tag,
            "runs": [run],
        }
        return self._post(url, data)

    def get_images_tags(self):
        if self.tb_port == 0:
            return {}
        url = f"http://localhost:{self.tb_port}/data/plugin/images/tags"
        return self._fetch(url)

    def get_images_images(self, run: str, tag: str, sample: int):
        if self.tb_port == 0:
            return []
        url = f"http://localhost:{self.tb_port}/data/plugin/images/images?run={run}&tag={tag}&sample={sample}"
        return self._fetch(url)

    def get_images_individualImage(self, blob_key: str):
        if self.tb_port == 0:
            return {}
        url = f"http://localhost:{self.tb_port}/data/plugin/images/individualImage?blob_key={blob_key}"
        return self._fetch(url)

    def get_audio_tags(self):
        if self.tb_port == 0:
            return {}
        url = f"http://localhost:{self.tb_port}/data/plugin/audio/tags"
        return self._fetch(url)

    def get_audio_audio(self, run: str, tag: str, sample: int):
        if self.tb_port == 0:
            return []
        url = f"http://localhost:{self.tb_port}/data/plugin/audio/audio?run={run}&tag={tag}&sample={sample}"
        return self._fetch(url)

    def get_audio_individualAudio(self, blob_key: str, content_type: str):
        if self.tb_port == 0:
            return {}
        url = f"http://localhost:{self.tb_port}/data/plugin/audio/individualAudio?blob_key={blob_key}&content_type={content_type}"
        return self._fetch(url)
