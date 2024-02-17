from dataclasses import dataclass
import os
import requests
import hashlib
from typing import Callable


from colab_easy_ui.Functions import JsonApiTaskProcessStatus, JsonApiTaskStatus, ProgressTaskProcessStatus, ProgressTaskStatus
from colab_easy_ui.const import is_running_on_colab


if is_running_on_colab():
    print("load tqdm for notebook")
    from tqdm.notebook import tqdm
else:
    print("load normal notebook")
    from tqdm import tqdm


@dataclass
class DownloadParams:
    display_name: str
    url: str
    saveTo: str
    hash: str | None
    position: int | None = None


@dataclass
class HashCheckResult:
    display_name: str
    url: str
    status: str
    message: str


class Downloader:
    def __init__(self, callback: (Callable[[JsonApiTaskStatus, ProgressTaskStatus], None]) | None = None):
        self.callback = callback
        self.params: list[DownloadParams] = []
        self.progresses = ProgressTaskStatus(processStatus={})

    # def pushItem(self, display_name: str, url: str, saveTo: str, hash: str | None):
    #     self.params.append(DownloadParams(display_name, url, saveTo, hash, len(self.params)))

    def pushItem(self, param: DownloadParams):
        position = len(self.params)
        param.position = position
        self.params.append(param)

    def updateProgress(self, display_name: str, url: str, n: int, total: int, status: JsonApiTaskProcessStatus):
        self.progresses.processStatus[display_name] = ProgressTaskProcessStatus(
            display_name=display_name,
            n=n if n >= 0 else self.progresses.processStatus[display_name].n,
            total=total if total >= 0 else self.progresses.processStatus[display_name].total,
            status=status,
            unit="byte",
        )
        if self.callback is not None:
            self.callback("RUNNING", self.progresses)

    def download(self):
        for p in self.params:
            self._download_and_check(p)
        # 以下、並列化を試行錯誤したが、うまくいかなかった残骸。 -> Threadingではなくてmultiprocessing.Poolでならいける説。要検証
        # import asyncio

        # tasks = [self._download_and_check(p) for p in self.params]
        # await asyncio.gather(*tasks)

        # with ThreadPoolExecutor() as pool:
        #     pool.map(self._downloadItem, self.params)
        # sleep(1)

        # for p in self.params:
        #     self.background_tasks.add_task(self._download_and_check, p)
        #     print(f"add task{p.saveTo}")
        #     # self._downloadItem(p)

        # import asyncio

        # # loop = asyncio.get_event_loop()
        # loop = asyncio.get_running_loop()
        # futures = [
        #     loop.run_in_executor(None, self._downloadItem, param)  # Noneはデフォルトのexecutorを使うことを意味します。
        #     # カスタムのexecutorを使う場合は、Noneの代わりにそれを指定します。
        #     for param in self.params
        # ]

        # # 全てのfutureが完了するのを待ちます
        # for future in asyncio.as_completed(futures):
        #     await future  # イテレートすることで、各ダウンロードの完了を待ちます。

    def _download_and_check(self, params: DownloadParams):
        self._downloadItem(params)
        self.check_hash(params)

    def _downloadItem(self, params: DownloadParams):
        display_name = params.display_name
        url = params.url
        saveTo = params.saveTo
        position = params.position
        dirname = os.path.dirname(saveTo)
        if dirname != "":
            os.makedirs(dirname, exist_ok=True)

        try:
            req = requests.get(url, stream=True, allow_redirects=True)

            content_length_header = req.headers.get("content-length")
            content_length = int(content_length_header) if content_length_header is not None else 1024 * 1024 * 1024

            progress_bar = tqdm(
                total=content_length if content_length > 0 else None,
                leave=False,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                position=position,
            )

            # with tqdm
            chunk_num = content_length // 1024
            callbacl_interval = chunk_num // 100
            with open(saveTo, "wb") as f:
                for i, chunk in enumerate(req.iter_content(chunk_size=1024)):
                    if chunk:
                        progress_bar.update(len(chunk))

                        if i % callbacl_interval == 0:
                            self.updateProgress(display_name, url, progress_bar.n, progress_bar.total, "RUNNING")
                            # print(f"{saveTo}, {i}/{chunk_num}")
                        f.write(chunk)

            self.updateProgress(display_name, url, progress_bar.n, progress_bar.total, "VALIDATING")

        except Exception as e:
            print(e)

    def check_hash(self, params: DownloadParams):
        if not os.path.exists(params.saveTo):
            self.updateProgress(params.display_name, params.url, -1, -1, "ERROR_DOWNLOAD_NOT_FOUND")

        with open(params.saveTo, "rb") as f:
            data = f.read()
            hash = hashlib.sha256(data).hexdigest()
            if hash != params.hash:
                self.updateProgress(params.display_name, params.url, -1, -1, "ERROR_INVALID_CHECKSUM")
                print(f"hash check failed: hash:{hash}, tested:{params.hash}")
            else:
                self.updateProgress(params.display_name, params.url, -1, -1, "DONE")

    # def check_hash(self):
    #     for target in self.params:
    #         if not os.path.exists(target.saveTo):
    #             self.updateProgress(target.display_name, target.url, -1, -1, "ERROR_DOWNLOAD_NOT_FOUND")
    #             continue

    #         with open(target.saveTo, "rb") as f:
    #             data = f.read()
    #             hash = hashlib.sha256(data).hexdigest()
    #             if hash != target.hash:
    #                 self.updateProgress(target.display_name, target.url, -1, -1, "ERROR_INVALID_CHECKSUM")
    #             else:
    #                 self.updateProgress(target.display_name, target.url, -1, -1, "DONE")
