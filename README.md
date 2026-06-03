# Image to ASCII

A powerful Python tool to convert images into beautiful ASCII art, supporting color, custom themes, edge detection, and HTML export.

## Features

- **Custom Themes**: Multiple character sets (default, simple, complex, binary, blocks, lines).
- **Color Support**: True-color terminal output and HTML export.
- **Image Enhancement**: Adjustable contrast and brightness.
- **Edge Detection**: Create "line drawing" versions of your images.
- **HTML Export**: Save high-fidelity colored ASCII art as shareable web pages.

## Requirements

- Python 3.10+
- Pillow (PIL)
- colorama

Install dependencies:

```bash
python -m pip install pillow colorama
```

## Usage

Run the script by passing the image path as an argument:

```bash
python ascii_converter.py path/to/your/image.jpg
```

### Options

| Alternative | Description | Default |
| :--- | :--- | :--- |
| `--width` | Width of the ASCII art | `100` |
| `--output` | Custom output file path | `ascii_image.txt` |
| `--color` | Enable colored output | `False` |
| `--theme` | character set (`default`, `simple`, `complex`, `binary`, `blocks`, `lines`) | `default` |
| `--contrast` | Contrast enhancement factor | `1.5` |
| `--brightness`| Brightness enhancement factor | `1.0` |
| `--edges` | Apply edge detection (best for line art) | `False` |
| `--html` | Export to a shareable HTML file | `False` |

### Examples

**Colored Output in Terminal:**
```bash
python ascii_converter.py image.jpg --color
```

**Line Art (Edge Detection) with Custom Width:**
```bash
python ascii_converter.py image.jpg --edges --width 150
```

**High-Fidelity Colored HTML Export:**
```bash
python ascii_converter.py image.jpg --color --html --contrast 2.0
```

**Binary Style conversion:**
```bash
python ascii_converter.py image.jpg --theme binary --width 80
```

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
