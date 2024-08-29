import json
import logging
import pathlib

import magic
import ollama
import pymupdf

from .interface import ABCProducer
from ..fs.tree import TreeObject


class OllamaProducer(ABCProducer):
    def __init__(self, host: str = "localhost",):
        super().__init__()
        self.host = host
        self.prompt = None
        self.model = None
        self.options = {}
        self.treat_pdf_as_images = False
        self._client = None

    def setup(
            self,
            prompt: str,
            model: str = "llama3",
            options: dict | None = None,
            treat_pdf_as_images: bool = False
    ):
        self.prompt = prompt
        self.model = model
        if options is not None:
            self.options = options
        if self.options is None:
            self.options = {}
        self.treat_pdf_as_images = treat_pdf_as_images

    @property
    def client(self) -> ollama.Client:
        if self._client is None:
            self._client = ollama.Client(
                host=self.host
            )
        return self._client

    def prepare_file(self, path: pathlib.Path):
        if self.model is None:
            raise ValueError("Model is not set")
        if self.prompt is None:
            raise ValueError("Prompt is not set")
        if self.options is None:
            raise ValueError("Options are not set")

        print(f"Preparing {path}")
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(path.as_posix())
        print(f"Detected mime type: {mime_type}")
        if mime_type.startswith("text"):
            with open(path, "r", encoding="utf-8") as f:
                result = self.client.generate(
                    model=self.model,
                    system=self.prompt,
                    prompt=f.read(),
                    options=self.options,
                    format="json"
                )
        elif mime_type.startswith("image"):
            with open(path, "rb") as f:
                result = self.client.generate(
                    model=self.model,
                    prompt=self.prompt,
                    images=[f.read()],
                    options=self.options,
                    format="json"
                )
        elif mime_type == "application/pdf" and self.treat_pdf_as_images:
            pdf_file = pymupdf.open(path.as_posix())
            if not pdf_file.is_pdf:
                logging.error(f"{path} is recognized as PDF but cannot be opened as such")
                return
            pdf_images = []
            for page in pdf_file:
                pdf_images.append(page.get_pixmap().tobytes())
            with open(path, "rb") as f:
                result = self.client.generate(
                    model=self.model,
                    prompt=self.prompt,
                    images=pdf_images,
                    options=self.options,
                    format="json"
                )
        elif mime_type == "application/pdf":
            pdf_file = pymupdf.open(path.as_posix())
            if not pdf_file.is_pdf:
                logging.error(f"{path} is recognized as PDF but cannot be opened as such")
                return
            pdf_text = ""
            for page in pdf_file:
                pdf_text += page.get_text() + "\nPAGE_BREAK\n"
            with open(path, "rb") as f:
                result = self.client.generate(
                    model=self.model,
                    system=self.prompt,
                    prompt=pdf_text,
                    options=self.options,
                    format="json"
                )
        else:
            raise ValueError(f"{mime_type} is not yet supported")
        print(f"Prepared {path}, result: {result}")
        self.prepared_files.append((path.as_posix(), result["response"]))

    def prepare_files(self, files_type: str | None = None):
        for file in self.files:
            if files_type is not None:
                mime = magic.Magic(mime=True)
                mime_type = mime.from_file(file.as_posix())
                if not mime_type.startswith(files_type):
                    continue
            if file.as_posix() in [f[0] for f in self.prepared_files]:
                continue
            try:
                self.prepare_file(file)
            except ValueError as e:
                logging.info(e)

    def produce(self) -> TreeObject:
        if self.model is None:
            raise ValueError("Model is not set")
        if self.prompt is None:
            raise ValueError("Prompt is not set")
        if self.options is None:
            raise ValueError("Options are not set")

        print("Producing")
        print(self.prepared_files)

        llama_response = self.client.generate(
            system=self.prompt,
            prompt=json.dumps(self.prepared_files),
            model=self.model,
            options=self.options,
            format="json"
        )["response"]

        print(llama_response)

        try:
            llama_response_json = json.loads(llama_response)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON response: {e}")
            logging.error(f"Response: {llama_response}")
            raise e

        for n, file in enumerate(llama_response_json.get("files", [])):
            src_path = pathlib.Path(file["src_path"])
            dst_path = pathlib.Path(file["dst_path"])
            if src_path.suffix != dst_path.suffix:
                dst_path = dst_path.with_suffix(src_path.suffix)
                llama_response_json["files"][n]["dst_path"] = dst_path.as_posix()

        return TreeObject.from_json(llama_response_json)


