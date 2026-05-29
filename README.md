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

The script currently uses a hardcoded image path inside [ascii_converter.py](ascii_converter.py):

```python
image_path = "image_path.jpg"
```

Replace that value with the image you want to convert, then run:

```bash
python ascii_converter.py
```

The ASCII output will be saved to `ascii_image.txt` in the project folder.

## Project Files

- [ascii_converter.py](ascii_converter.py) - main conversion script
- [README.md](README.md) - project overview and usage
- [.gitignore](.gitignore) - ignores the virtual environment and generated files

## Notes

- If you want to keep the generated ASCII output, copy it before running the script again.
- If you want to use a different input image, update the `image_path` variable in the script.
