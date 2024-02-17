# !/usr/bin/env python3

__version__="0.1.1"

import argparse, json, os.path, urllib.request
from tqdm import tqdm

def get_file_size(url):
    with urllib.request.urlopen(url) as response:
        size = int(response.headers['Content-Length'])
    return size

def clone_file(url):
    try:
        file_size = get_file_size(url)
        filename = os.path.basename(url)
        # Download the file with progress
        with urllib.request.urlopen(url) as response, \
             open(filename, 'wb') as file, \
             tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024, desc=f'Downloading {filename}') as pbar:
            # Download in chunks and update the progress bar
            chunk_size = 1024  # 1 KB
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                file.write(chunk)
                pbar.update(len(chunk))
        print(f"File cloned successfully and saved as '{filename}' in the current directory.")
    except Exception as e:
        print(f"Error: {e}")

def read_json_file(file_path):
    response = urllib.request.urlopen(file_path)
    data = json.loads(response.read())
    # with open(file_path, 'r') as file:
        # data = json.load(file)
    return data

def extract_names(data):
    for idx, entry in enumerate(data, start=1):
        print(f'{idx}. {entry["name"]}')

def handle_user_input(data):
    while True:
        user_choice = input(f"Enter your choice (1 to {len(data)}) or 'q' to quit: ")
        if user_choice.lower() == 'q':
            break
        try:
            index = int(user_choice)
            if 1 <= index <= len(data):
                source_url = data[index - 1]["url"]
                clone_file(source_url)
                break
            else:
                print("Invalid selection. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def __init__():
    parser = argparse.ArgumentParser(description="cgg will execute different functions based on command-line arguments")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand", help="choose a subcommand:")
    # Subparser for 'clone [URL]' subcommand
    clone_parser = subparsers.add_parser('clone', help='download a GGUF file/model from URL')
    clone_parser.add_argument('url', type=str, help='URL to download from (i.e., egg clone [url])')
    # Subparser for 'menu/cpp/c/gpp/g/s' subcommand
    subparsers.add_parser('menu', help='connector selection list:')
    subparsers.add_parser('cpp', help='cpp connector')
    subparsers.add_parser('gpp', help='gpp connector')
    subparsers.add_parser('c', help='c connector')
    subparsers.add_parser('g', help='g connector')
    subparsers.add_parser('s', help='sample GGUF list (ready)')
    args = parser.parse_args()

    if args.subcommand == 'clone':
        clone_file(args.url)
    elif args.subcommand == 's':
        file_path = "https://raw.githubusercontent.com/calcuis/gguf-connector/main/src/gguf_connector/data.json"
        # file_path = os.path.join(os.path.dirname(__file__), 'data.json')
        json_data = read_json_file(file_path)
        print("Please select a GGUF file to download:")
        extract_names(json_data)
        handle_user_input(json_data)
    elif args.subcommand == 'menu':
        from gguf_connector import menu
    elif args.subcommand == 'cpp':
        from gguf_connector import cpp
    elif args.subcommand == 'c':
        from gguf_connector import c
    elif args.subcommand == 'gpp':
        from gguf_connector import gpp
    elif args.subcommand == 'g':
        from gguf_connector import g
