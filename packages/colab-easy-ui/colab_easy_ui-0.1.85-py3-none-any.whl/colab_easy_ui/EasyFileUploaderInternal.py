import os
import shutil

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi import UploadFile, File, Form
from fastapi import APIRouter

from colab_easy_ui.data.Response import EasyFileUploaderResponse


class EasyFileUploader:
    def __init__(self, upload_dir: str):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)
        self.allowed_filenames: dict[str, str] | None = None
        self.file_titles: list[str] | None = None
        self.router = APIRouter()
        self.router.add_api_route("/uploader_info", self.get_info, methods=["GET"])
        self.router.add_api_route("/uploader_upload_file", self.post_upload_file, methods=["POST"])
        self.router.add_api_route("/uploader_concat_uploaded_files", self.post_concat_uploaded_file, methods=["POST"])

    def set_allowed_filenames(self, filenames: dict[str, str] | None):  # filenamestitle, filename
        """
        upload 可能なファイルを指定する。

        Args:
            filenames (dict[str, str] | None): "key:ファイルのタイトル"と"val:アップロード可能なファイル名"のペアの辞書。タイトルはアプリケーション上に表示される名前を想定。valが実際に許容されるファイル名。


        """
        self.allowed_filenames = filenames

    def get_info(self):
        try:
            response = EasyFileUploaderResponse(
                status="OK",
                message="",
                allowed_filenames=self.allowed_filenames,
            )
            json_compatible_item_data = jsonable_encoder(response)
            return JSONResponse(content=json_compatible_item_data)
        except Exception as e:
            response = EasyFileUploaderResponse(
                status="NG",
                message=f"Exception: {e}",
            )
            json_compatible_item_data = jsonable_encoder(response)
            return JSONResponse(content=json_compatible_item_data)

    def _sanitize_filename(self, filename: str) -> str:
        if self.allowed_filenames is not None:
            if filename not in self.allowed_filenames.values():
                print(f"filename {filename} is not allowed. Allowed filenames are {self.allowed_filenames}")
                raise RuntimeError
            # else:
            #     print(f"filename {filename} is allowed. Allowed filenames are {self.allowed_filenames}")

        safe_filename = os.path.basename(filename)
        max_length = 255
        if len(safe_filename) > max_length:
            file_root, file_ext = os.path.splitext(safe_filename)
            safe_filename = file_root[: max_length - len(file_ext)] + file_ext

        return safe_filename

    #######################################
    # Upload File
    # TEST:
    #  curl -X POST -F "filename=data1" -F "index=0" -F "file=@test_data/data0.txt" http://localhost:8001/upload_file
    #  curl -X POST -F "filename=data1" -F "index=1" -F "file=@test_data/data0.txt" http://localhost:8001/upload_file
    #  curl -X POST -F "filename=data1" -F "index=2" -F "file=@test_data/data2.txt" http://localhost:8001/upload_file
    #######################################
    def post_upload_file(
        self,
        file: UploadFile = File(...),
        filename: str = Form(...),
        index: int = Form(...),
    ):
        try:
            res = self._upload_file(self.upload_dir, file, filename, index)
            json_compatible_item_data = jsonable_encoder(res)
            return JSONResponse(content=json_compatible_item_data)
        except Exception as e:
            print("[Voice Changer] post_upload_file ex:", e)

    def _upload_file(self, upload_dirname: str, file: UploadFile, filename: str, index: int):
        if file and filename:
            try:
                filename = self._sanitize_filename(filename)
            except RuntimeError:
                response = EasyFileUploaderResponse(
                    status="NG",
                    message=f"filename {filename} is not allowed. Allowed filenames are {self.allowed_filenames}",
                )
                json_compatible_item_data = jsonable_encoder(response)
                return JSONResponse(content=json_compatible_item_data)

            filename = f"{filename}_{index}"
            fileobj = file.file
            target_path = os.path.join(upload_dirname, filename)
            target_dir = os.path.dirname(target_path)
            os.makedirs(target_dir, exist_ok=True)
            upload_dir = open(target_path, "wb+")
            shutil.copyfileobj(fileobj, upload_dir)
            upload_dir.close()

            response = EasyFileUploaderResponse(
                status="OK",
                message=f"uploaded files {filename} ",
            )
            json_compatible_item_data = jsonable_encoder(response)
            return JSONResponse(content=json_compatible_item_data)

        else:
            response = EasyFileUploaderResponse(
                status="NG",
                message="no file found",
            )
            json_compatible_item_data = jsonable_encoder(response)
            return JSONResponse(content=json_compatible_item_data)

    #######################################
    # Concat File
    # TEST:
    #  curl -X POST -F "filename=data1"  -F "filenameChunkNum=3" http://localhost:8001/concat_uploaded_file
    #######################################
    def post_concat_uploaded_file(self, filename: str = Form(...), filenameChunkNum: int = Form(...)):
        try:
            res = self._concat_file_chunks(self.upload_dir, filename, filenameChunkNum, self.upload_dir)
            json_compatible_item_data = jsonable_encoder(res)
            return JSONResponse(content=json_compatible_item_data)
        except Exception as e:
            print("[Voice Changer] post_concat_uploaded_file ex:", e)

    def _concat_file_chunks(self, upload_dirname: str, filename: str, chunkNum: int, dest_dirname: str):
        try:
            filename = self._sanitize_filename(filename)
        except RuntimeError:
            response = EasyFileUploaderResponse(
                status="NG",
                message=f"filename {filename} is not allowed. Allowed filenames are {self.allowed_filenames}",
            )
            json_compatible_item_data = jsonable_encoder(response)
            return JSONResponse(content=json_compatible_item_data)

        target_path = os.path.join(upload_dirname, filename)  # filenameにサブフォルダ名が入っている場合への対策として、joinしてからdirnameする <- サニタイズでサブフォルダを削除する仕様に変更したため意味はなくなった。
        target_dir = os.path.dirname(target_path)
        os.makedirs(target_dir, exist_ok=True)

        if os.path.exists(target_path):
            os.remove(target_path)
        with open(target_path, "ab") as out:
            for i in range(chunkNum):
                chunkName = f"{filename}_{i}"
                chunk_file_path = os.path.join(upload_dirname, chunkName)
                stored_chunk_file = open(chunk_file_path, "rb")
                out.write(stored_chunk_file.read())
                stored_chunk_file.close()
                os.remove(chunk_file_path)
            out.close()

        response = EasyFileUploaderResponse(
            status="OK",
            message=f"concat files {filename} ",
        )
        json_compatible_item_data = jsonable_encoder(response)
        return JSONResponse(content=json_compatible_item_data)
