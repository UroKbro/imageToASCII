# Image to ASCII

Convert an image into plain text ASCII art.

## What It Does

The script in [ascii_converter.py](ascii_converter.py) opens an image, turns it into grayscale, maps the pixels to ASCII characters, and writes the result to `ascii_image.txt`.

## Requirements

- Python 3.14
- Pillow
- colorama

Install dependencies inside your virtual environment:

```bash
python -m pip install pillow colorama
```

## Setup

1. Activate the virtual environment:

```bash
source .venv/bin/activate
```
ies:

```bash
python -m pip install pillow colorama
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
*   `--color`: Enable colored output in the terminal.

Example:
```bash
python ascii_converter.py my_photo.jpg --width 150 --color
```

## Project Files

- [ascii_converter.py](ascii_converter.py) - main conversion script
- [README.md](README.md) - project overview and usage
- [.gitignore](.gitignore) - ignores the virtual environment and generated files

## Notes

- The `--color` option uses 24-bit ANSI escape codes, which work in most modern terminals (VS Code terminal, iTerm2, etc.).
- When saving color output to a file, the file will contain ANSI escape codes. To view it with color later, use `cat` in your terminal: `cat ascii_image.txt`
- If you want to use a different input image, update the `image_path` variable in the script.
