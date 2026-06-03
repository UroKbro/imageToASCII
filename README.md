# Image to ASCII

A powerful Python tool to convert images into beautiful ASCII art, supporting color, custom themes, edge detection, and HTML export.

## Features

- **Custom Themes**: Multiple character sets (default, simple, complex, binary, blocks, lines).
- **Color Support**: True-color terminal output and HTML export.
- **Image Enhancement**: Adjustable contrast and brightness.
- **Edge Detection**: Create "line drawing" versions of your images.
- **HTML Export**: Save high-fidelity colored ASCII art as shareable web pages.
- **Webcam Mode**: Render live ASCII video from your webcam in the terminal.

## Requirements

- Python 3.10+
- Pillow (PIL)
- colorama
- opencv-python (for webcam mode)

Install dependencies:

```bash
python -m pip install pillow colorama opencv-python
```

## Usage

Run the script by passing the image path as an argument:

```bash
python ascii_converter.py path/to/your/image.jpg
```

### Options

| Option | Description | Default |
| :--- | :--- | :--- |
| `--width` | Width of the ASCII art | `100` |
| `--height-scale` | Height scaling factor for ASCII | `0.55` |
| `--output` | Custom output file path | `ascii_image.txt` |
| `--color` | Enable colored output (image mode only) | `False` |
| `--theme` | character set (`default`, `simple`, `complex`, `binary`, `blocks`, `lines`) | `default` |
| `--contrast` | Contrast enhancement factor | `1.5` |
| `--brightness`| Brightness enhancement factor | `1.0` |
| `--edges` | Apply edge detection (best for line art) | `False` |
| `--edge-blur` | Edge detection blur radius | `0.5` |
| `--edge-contrast` | Edge detection contrast boost | `3.0` |
| `--edge-brightness` | Edge detection brightness boost | `1.5` |
| `--html` | Export to a shareable HTML file | `False` |
| `--webcam` | Use live webcam input | `False` |
| `--camera` | Webcam index | `0` |
| `--fps` | Target frames per second for webcam mode | `30` |
| `--no-clear` | Do not clear the terminal between frames | `False` |
| `--no-alt-buffer` | Disable alternate screen buffer in webcam mode | `False` |
| `--record` | Record webcam ASCII to GIF/MP4 (imageio) | (none) |
| `--record-fps` | FPS for recorded output | (matches `--fps`) |
| `--record-seconds` | Record duration in seconds | (unlimited) |

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

**Live Webcam ASCII:**
```bash
python ascii_converter.py --webcam --width 120 --fps 20
```

Webcam mode is monochrome only, and trailing space characters are avoided to reduce empty gaps.

**Tune Edge Detection for Webcam:**
```bash
python ascii_converter.py --webcam --edges --edge-blur 0.8 --edge-contrast 4.0 --edge-brightness 1.8
```

**Record a Short GIF (5 seconds):**
```bash
python ascii_converter.py --webcam --record out.gif --record-seconds 5
```

Press Ctrl+C to stop the webcam feed.
You can also press `q` to exit webcam mode.

## Project Files

- [ascii_converter.py](ascii_converter.py) - main conversion script
- [README.md](README.md) - project overview and usage
- [.gitignore](.gitignore) - ignores the virtual environment and generated files

## Notes

- The `--color` option uses 24-bit ANSI escape codes, which work in most modern terminals (VS Code terminal, iTerm2, etc.).
- When saving color output to a file, the file will contain ANSI escape codes. To view it with color later, use `cat` in your terminal: `cat ascii_image.txt`
- If you want to use a different input image, update the `image_path` variable in the script.
