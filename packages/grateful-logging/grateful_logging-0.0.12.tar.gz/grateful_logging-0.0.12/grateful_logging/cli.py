import os
import argparse


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXAMPLE_CONFIG_FILE = os.path.join(BASE_DIR, "assets/config-example.json")


def create_config_file(filename):
    with open(EXAMPLE_CONFIG_FILE, "r", encoding="utf-8") as f:
        config = f.read()

    with open(filename, "w", encoding="utf-8") as f:
        f.write(config)


def main():
    parser = argparse.ArgumentParser(description="Create an example config file.")
    parser.add_argument(
        "--filename",
        help="Specify the name of the config file. If not provided, default is 'config.json'.",
        default="logger-config.json",
    )

    args = parser.parse_args()
    create_config_file(args.filename)
