import argparse
import pathlib

from app import demo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", type=str, help="Command to execute")
    parser.add_argument("path", type=pathlib.Path, help="Path to directory")
    parser.add_argument("--producer", type=str, help="Producer to use: llama/groq", default="llama")
    parser.add_argument("--apikey", type=str, help="API key for Groq", default=None)
    args = parser.parse_args()
    print(args.command, args.path)
    if args.command == "demo":
        demo(args.path, args.producer, args.apikey)
    else:
        print("Unknown command")


if __name__ == "__main__":
    main()
