# Image to ASCII

Convert an image into plain text ASCII art.

## What It Does

The script in [ascii_converter.py](ascii_converter.py) opens an image, turns it into grayscale, maps the pixels to ASCII characters, and writes the result to `ascii_image.txt`.

## Requirements

- Python 3.14
- Pillow

Install Pillow inside your virtual environment:

```bash
python -m pip install pillow
```

## Setup

1. Activate the virtual environment:

```bash
source .venv/bin/activate
```

2. Install the dependency:

```bash
python -m pip install pillow
```

## Usage

Run the script by passing the image path as an argument:

```bash
python ascii_converter.py path/to/your/image.jpg
```

### Options

*   `--width`: Set the width of the ASCII art (default is 100).
*   `--output`: Specify a custom output file (default is `ascii_image.txt`).

Example:
```bash
python ascii_converter.py my_photo.jpg --width 150 --output my_art.txt
```

## Project Files

- [ascii_converter.py](ascii_converter.py) - main conversion script
- [README.md](README.md) - project overview and usage
- [.gitignore](.gitignore) - ignores the virtual environment and generated files

## Notes

- If you want to keep the generated ASCII output, copy it before running the script again.
- If you want to use a different input image, update the `image_path` variable in the script.
