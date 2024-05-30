import json
import logging
import pathlib

import anthropic
import magic
import ollama

from .interface import ABCProducer
from ..fs.tree import TreeObject


class ClaudeProducer(ABCProducer):
    def __init__(self, host: str = "https://api.anthropic.com", apikey: str = None):
        super().__init__()
        self.host = host
        self.prompt = None
        self.model = None
        self.options = {}
        self._client = None
        self.apikey = apikey

    def setup(
            self,
            prompt: str,
            model: str = "claude-3-opus-20240229",
            options: dict | None = None,
    ):
        self.prompt = prompt
        self.model = model
        if options is not None:
            self.options = options
        if self.options is None:
            self.options = {}

    @property
    def client(self) -> anthropic.Client:
        if self._client is None:
            self._client = anthropic.Client(
                base_url=self.host,
                api_key=self.apikey
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
                result = self.client.messages.create(
                    messages=[
                        {"content": f.read(), "role": "user"},
                    ],
                    model=self.model,
                    system=self.prompt,
                    **self.options
                )
        elif mime_type.startswith("image"):
            with open(path, "rb") as f:
                result = self.client.messages.create(
                    messages=[
                        {"content": [{
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime_type,
                                "data": f.read()
                            }
                        }], "role": "user"}
                    ],
                    model=self.model,
                    system=self.prompt,
                    **self.options
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

        claude_response = self.client.messages.create(
            messages=[
                {"content": json.dumps(self.prepared_files), "role": "user"}
            ],
            system=self.prompt,
            model=self.model,
            **self.options
        ).response.read()

        try:
            calude_response_json = json.loads(claude_response)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON response: {e}")
            logging.error(f"Response: {claude_response}")
            raise e

        return TreeObject.from_json(claude_response_json)


