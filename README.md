# Image to ASCII

A powerful Python tool to convert images into beautiful ASCII art, supporting color, custom themes, edge detection, and HTML export.

## Features

- **Custom Themes**: Multiple character sets (default, simple, complex, binary, blocks, lines).
- **Color Support**: True-color terminal output and HTML export.
- **Image Enhancement**: Adjustable contrast and brightness.
- **Edge Detection**: Create "line drawing" versions of your images.
- **HTML Export**: Save high-fidelity colored ASCII art as shareable web pages.
- **Webcam Mode**: Render live ASCII video from your webcam in the terminal.
- **Virtual Camera**: Live-zoom and pan around the ASCII webcam feed using keyboard controls.
- **Matrix Drip Effect**: Falling green characters stream down and interact with your silhouette.
- **Motion Blur**: Add cinematic frame blending to your webcam feed.
- **Braille Mode**: 2x4 pixel Unicode Braille rendering for high-resolution output.
- **Glitch + Audio Reactivity**: Live glitch effects with optional microphone-driven distortion.

## Requirements

- Python 3.10+
- Pillow (PIL)
- colorama
- opencv-python (for webcam mode)
- sounddevice + numpy (optional, for audio-reactive glitches)

Install dependencies:

```bash
python -m pip install pillow colorama opencv-python

# Optional: audio reactivity
python -m pip install sounddevice numpy
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
| `--height-scale` | Height scaling factor for ASCII | `0.55` (or `1.0` in braille mode) |
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
| `--braille` | Use high-resolution braille mode (2x4 pixel mapping) | `False` |
| `--braille-threshold` | Threshold for braille dots (0-255) | `128` |
| `--glitch` | Enable live glitch effects in webcam mode | `False` |
| `--glitch-intensity` | Glitch intensity | `0.25` |
| `--glitch-slice-height` | Max height of glitch slices | `2` |
| `--glitch-max-shift` | Max horizontal shift for glitches | `10` |
| `--glitch-scramble` | Chance to scramble a line | `0.03` |
| `--audio-reactive` | Make glitches react to microphone input | `False` |
| `--audio-gain` | Audio reactivity gain | `1.5` |
| `--audio-device` | Audio input device index for reactivity | (none) |
| `--motion-blur` | Enable motion blur in webcam mode | `False` |
| `--motion-blur-strength` | Motion blur strength (0.0 to 1.0) | `0.5` |
| `--matrix` | Enable Matrix digital rain effect in webcam mode | `False` |

### Keyboard Controls (Webcam Mode)

- `q` / `Q`: Quit
- `c` / `C`: Toggle color
- `+` / `=`: Zoom in
- `-`: Zoom out
- `Arrow Keys`: Pan camera (when zoomed in)
- `0`: Reset camera pan and zoom

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
Braille mode renders a 2x4 pixel grid per character for higher visual resolution.

**Tune Edge Detection for Webcam:**
```bash
python ascii_converter.py --webcam --edges --edge-blur 0.8 --edge-contrast 4.0 --edge-brightness 1.8
```

**Record a Short GIF (5 seconds):**
```bash
python ascii_converter.py --webcam --record out.gif --record-seconds 5
```

**High-Resolution Braille Output:**
```bash
python ascii_converter.py image.jpg --braille --width 140
```

**Live Glitch + Audio Reactivity:**
```bash
python ascii_converter.py --webcam --glitch --audio-reactive --glitch-intensity 0.35
```

**Matrix Drip Effect:**
```bash
python ascii_converter.py --webcam --matrix
```

**Motion Blur Trail Effect:**
```bash
python ascii_converter.py --webcam --motion-blur --motion-blur-strength 0.8
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
