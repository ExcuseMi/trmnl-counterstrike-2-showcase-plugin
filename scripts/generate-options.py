#!/usr/bin/env python3
"""
Download CS2 item data from CSGO-API and split into manageable chunks.
Place this script in the root/scripts folder.
"""

import json
import os
import sys
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

# Base URL for the API
BASE_URL = "https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/en"

# Files to download
FILES = [
    "agents.json",
    "base_weapons.json",
    "collectibles.json",
    "collections.json",
    "crates.json",
    "graffiti.json",
    "highlights.json",
    "keychains.json",
    "keys.json",
    "music_kits.json",
    "patches.json",
    "skins.json",
    "stickers.json",
    "stickers_slab.json",
    "tools.json",
]

# Maximum file size in bytes (100KB)
MAX_FILE_SIZE = 80 * 1024

# Mapping of file types to display names
DISPLAY_NAMES = {
    "skins": "Skins",
    "crates": "Crates",
    "collectibles": "Collectibles",
    "keys": "Keys",
    "stickers": "Stickers",
    "keychains": "Keychains",
    "stickers_slab": "Sticker Slabs",
    "agents": "Agents",
    "patches": "Patches",
    "graffiti": "Graffiti",
    "music_kits": "Music Kits",
    "base_weapons": "Base Weapons",
    "collections": "Collections",
    "highlights": "Highlights",
    "tools": "Tools"
}


def download_file(filename):
    """Download a JSON file from the API."""
    url = f"{BASE_URL}/{filename}"
    print(f"Downloading {filename}...")

    try:
        with urlopen(url) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except URLError as e:
        print(f"Error downloading {filename}: {e}")
        return None

def generate_item_types_json(file_counts, output_path):
    """Generate the item_types.json file with dynamic file counts."""
    item_types = []

    # Add options for each file type that was successfully downloaded
    for typename, count in sorted(file_counts.items()):
        if typename in DISPLAY_NAMES:
            display_name = DISPLAY_NAMES[typename]
            value = f"{typename}|{count}"
            item_types.append({
                display_name:
                value
            })

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(item_types, f, ensure_ascii=False, separators=(',', ':'))

    print(f"\nGenerated {output_path}")
def split_json_data(data, typename, output_dir):
    """Split JSON data into chunks under MAX_FILE_SIZE."""
    # If data is a list, split by items
    if isinstance(data, list):
        chunks = []
        current_chunk = []
        current_size = 2  # Account for [] brackets

        for item in data:
            item_json = json.dumps(item, ensure_ascii=False)
            item_size = len(item_json.encode('utf-8')) + 1  # +1 for comma

            # If single item exceeds max size, put it in its own chunk
            if item_size > MAX_FILE_SIZE - 2:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = []
                    current_size = 2
                chunks.append([item])
                continue

            # If adding this item would exceed max size, start new chunk
            if current_size + item_size > MAX_FILE_SIZE:
                chunks.append(current_chunk)
                current_chunk = [item]
                current_size = 2 + item_size
            else:
                current_chunk.append(item)
                current_size += item_size

        # Add remaining items
        if current_chunk:
            chunks.append(current_chunk)

    # If data is a dict, split by top-level keys if necessary
    elif isinstance(data, dict):
        # Try to keep it as one file first
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        if len(json_str.encode('utf-8')) <= MAX_FILE_SIZE:
            chunks = [data]
        else:
            # Split by keys
            chunks = []
            current_chunk = {}
            current_size = 2  # Account for {} brackets

            for key, value in data.items():
                item_json = json.dumps({key: value}, ensure_ascii=False)
                item_size = len(item_json.encode('utf-8'))

                if item_size > MAX_FILE_SIZE - 2:
                    if current_chunk:
                        chunks.append(current_chunk)
                        current_chunk = {}
                        current_size = 2
                    chunks.append({key: value})
                    continue

                if current_size + item_size > MAX_FILE_SIZE:
                    chunks.append(current_chunk)
                    current_chunk = {key: value}
                    current_size = 2 + item_size
                else:
                    current_chunk[key] = value
                    current_size += item_size

            if current_chunk:
                chunks.append(current_chunk)
    else:
        chunks = [data]

    # Save chunks
    os.makedirs(output_dir, exist_ok=True)
    for i, chunk in enumerate(chunks):
        output_file = output_dir / f"{i}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, ensure_ascii=False, indent=2)

        file_size = output_file.stat().st_size
        print(f"  Created {output_file} ({file_size / 1024:.1f} KB)")

    return len(chunks)


def generate_options_yml(file_counts, output_path):
    """Generate the options.yml file with dynamic file counts."""
    yml_content = """- keyname: about
  name: About This Plugin
  field_type: author_bio
  github_url: https://github.com/ExcuseMi/trmnl-counterstrike-2-showcase-plugin
  description: "Showcase every available item in Counter-Strike 2, including skins, crates, collectibles, music kits, and more."
- keyname: item_types
  field_type: select
  name: Item Types to Display
  description: "Select all the item types you want to display."
  options:
"""

    # Add options for each file type that was successfully downloaded
    for typename, count in sorted(file_counts.items()):
        if typename in DISPLAY_NAMES:
            display_name = DISPLAY_NAMES[typename]
            max_index = count - 1  # 0-indexed
            yml_content += f'    - "{display_name}": {typename}|{max_index+1}\n'

    yml_content += """  multiple: true
  help_text: "Use <kbd>⌘</kbd>+<kbd>click</kbd> or <kbd>Ctrl</kbd>+<kbd>click</kbd> to select multiple item types.<br />Leave empty to show all item types."
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(yml_content)

    print(f"\nGenerated {output_path}")


def main():
    # Determine the root directory (parent of scripts folder)
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    data_dir = root_dir / "data"

    print(f"Root directory: {root_dir}")
    print(f"Data directory: {data_dir}")
    print()

    file_counts = {}

    for filename in FILES:
        typename = filename.replace('.json', '')

        # Download the file
        data = download_file(filename)
        if data is None:
            continue

        # Split and save the data
        output_dir = data_dir / typename
        chunk_count = split_json_data(data, typename, output_dir)
        file_counts[typename] = chunk_count

        print(f"  Split into {chunk_count} file(s)\n")
    item_types_path = data_dir / "item_types.json"
    generate_item_types_json(file_counts, item_types_path)
    # Generate options.yml
    options_path = data_dir / "options.yml"
    generate_options_yml(file_counts, options_path)

    print("\nDownload and split complete!")
    print(f"Total file types processed: {len(file_counts)}")


if __name__ == "__main__":
    main()