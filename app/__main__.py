import argparse
import logging
import pathlib
import sys

from app import demo, IMAGE_SUPPORT_PRODUCERS, move_file


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", type=str, help="Command to execute")
    parser.add_argument("path", type=pathlib.Path, help="Path to directory")
    parser.add_argument("--producer", type=str, help="Producer to use: ollama/groq/claude/openai", default="ollama")
    parser.add_argument("--apikey", type=str, help="API key for Groq/Claude/OpenAI", default=None)
    parser.add_argument("--text-model", type=str, help="Text model to use", default=None)
    parser.add_argument("--image-model", type=str, help="Image model to use", default=None)
    args = parser.parse_args()
    print(args.command, args.path)

    if args.producer not in IMAGE_SUPPORT_PRODUCERS and "--image-model" in sys.argv:
        logging.warning(f"--image-model is only supported with the {' and '.join(IMAGE_SUPPORT_PRODUCERS)} "
                        f"producers, ignoring")

    if args.text_model is None:
        if args.producer == "ollama":
            args.text_model = "llama3"
        elif args.producer == "claude":
            args.text_model = "claude-3-haiku-20240307"
        elif args.producer == "groq":
            args.text_model = "llama3-70b-8192"
        elif args.producer == "openai":
            args.text_model = "gpt-4o"  # "gpt-3.5-turbo-1106"
    if args.image_model is None:
        if args.producer == "ollama":
            args.image_model = "llava"
        elif args.producer == "claude":
            args.image_model = "claude-3-haiku-20240307"

    if args.command == "demo":
        treedict = demo(args.path, args.producer, args.text_model, args.image_model, args.apikey)
    else:
        print("Unknown command")

    for file in treedict['files']:
        move_file(args.path, file)
    
if __name__ == "__main__":
    main()
