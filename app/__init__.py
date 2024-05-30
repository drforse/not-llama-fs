import pathlib

from not_llama_fs.producers.claude_producer import ClaudeProducer
from not_llama_fs.producers.groq_producer import GroqProducer
from not_llama_fs.producers.llama_producer import LlamaProducer
from not_llama_fs.producers.openai_producer import OpenAIProducer


def demo(path: pathlib.Path, producer: str = "llama", apikey: str = None):
    if not path.exists():
        raise ValueError(f"Path {path} does not exist")

    with open("file_process_prompt.txt", "r") as f:
        prompt = f.read()

    with open("tree_generation_prompt.txt", "r") as f:
        final_prompt = f.read()

    print(f"Using producer {producer}")
    options = {}
    produce_options = {}
    if producer == "llama":
        producer = LlamaProducer(host="localhost")
        model = "llama3"
        options = {"num_tokens": 128}
        produce_options = {"num_tokens": -1}
    elif producer == "groq":
        producer = GroqProducer(api_key=apikey)
        model = "llama3-70b-8192"
    elif producer == "openai":
        producer = OpenAIProducer(api_key=apikey)
        model = "gpt-3.5-turbo-1106"
    elif producer == "claude":
        producer = ClaudeProducer(apikey=apikey)
        model = "claude-3-haiku-20240307"
        options = {"max_tokens": 128}
        produce_options = {"max_tokens": 4096}
    else:
        raise ValueError(f"Unknown producer {producer}")

    producer.load_directory(path)
    if producer == "llama":
        producer.setup(prompt, model="llava", options=options)
        producer.prepare_files("image")
    elif producer == "claude":
        producer.setup(prompt, model=model, options=options)
        producer.prepare_files()
    producer.setup(prompt, model=model, options=options)
    producer.prepare_files("text")
    producer.setup(final_prompt, model=model, options=produce_options)
    tree = producer.produce()
    print(tree)
