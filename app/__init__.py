import pathlib

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
        apikey: str = None
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
        model = 'llama3'
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

    producer.setup(prompt, model=text_model, options=options)
    producer.prepare_files_llamaindex(path)
    producer.setup(final_prompt, model=model, options=produce_options)
    treedict, tree = producer.produce() # issue here with how the model is producing , dictionaries for metadata is not consistent at all
    print(tree)

    return treedict
