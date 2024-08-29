import pathlib

from not_llama_fs.fs.fs_writer import FsWriter, LocalDiskFsWriter
from not_llama_fs.producers.claude_producer import ClaudeProducer
from not_llama_fs.producers.groq_producer import GroqProducer
from not_llama_fs.producers.ollama_producer import OllamaProducer
from not_llama_fs.producers.openai_producer import OpenAIProducer

IMAGE_SUPPORT_PRODUCERS = ["ollama", "claude"]


def demo(
        path: pathlib.Path,
        producer_name: str = "ollama",
        text_model: str = "llama3",
        image_model: str = "llava",
        apikey: str = None,
        treat_pdf_as_images: bool = False
):
    tree = _get_tree(path, producer_name, text_model, image_model, apikey, treat_pdf_as_images)
    print(tree)


def create_local_disk_fs(
        path: pathlib.Path,
        dest_path: pathlib.Path,
        producer_name: str = "ollama",
        text_model: str = "llama3",
        image_model: str = "llava",
        apikey: str = None,
        treat_pdf_as_images: bool = False,
        move: bool = False
):
    tree = _get_tree(path, producer_name, text_model, image_model, apikey, treat_pdf_as_images)
    print(tree)
    print(f"Writing tree to {dest_path}")
    dest_path.mkdir(exist_ok=True, parents=True)
    LocalDiskFsWriter(dest_path, move).write_tree(tree)


def _get_tree(
        path: pathlib.Path,
        producer_name: str = "ollama",
        text_model: str = "llama3",
        image_model: str = "llava",
        apikey: str = None,
        treat_pdf_as_images: bool = False
):
    if not path.exists():
        raise ValueError(f"Path {path} does not exist")

    with open("file_process_prompt.txt", "r") as f:
        prompt = f.read()

    with open("tree_generation_prompt.txt", "r") as f:
        final_prompt = f.read()

    print(f"Using producer {producer_name}")
    options = {}
    produce_options = {}
    if producer_name == "ollama":
        producer = OllamaProducer(host="localhost")
        options = {"num_predict": 128}
        produce_options = {"num_predict": -1}
    elif producer_name == "groq":
        producer = GroqProducer(api_key=apikey)
    elif producer_name == "openai":
        producer = OpenAIProducer(api_key=apikey)
    elif producer_name == "claude":
        producer = ClaudeProducer(apikey=apikey)
        options = {"max_tokens": 128}
        produce_options = {"max_tokens": 4096}
    else:
        raise ValueError(f"Unknown producer {producer_name}")

    producer.load_directory(path)

    if producer_name in IMAGE_SUPPORT_PRODUCERS:
        producer.setup(prompt, model=image_model, options=options)
        producer.prepare_files("image")

    producer.setup(prompt, model=text_model, options=options, treat_pdf_as_images=treat_pdf_as_images)
    producer.prepare_files()
    producer.setup(final_prompt, model=text_model, options=produce_options)
    return producer.produce()
