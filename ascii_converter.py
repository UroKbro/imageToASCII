from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import argparse
import random
import select
import signal
import sys
import termios
import threading
import time
import tty
from colorama import Style, init

# Initialize colorama for Windows support
init()

# Define character sets for different themes
THEMES = {
    "default": ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."],
    "simple": ["#", "S", "+", ".", " "],
    "complex": list("$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\\\"^`'. "),
    "binary": ["1", "0"],
    "blocks": ["█", "▓", "▒", "░", " "],
    "lines": ["#", "+", "/", "\\", "|", "-", "_", ".", " "]
}

BRAILLE_DOT_BITS = {
    (0, 0): 0x01,  # dot 1
    (0, 1): 0x02,  # dot 2
    (0, 2): 0x04,  # dot 3
    (0, 3): 0x40,  # dot 7
    (1, 0): 0x08,  # dot 4
    (1, 1): 0x10,  # dot 5
    (1, 2): 0x20,  # dot 6
    (1, 3): 0x80,  # dot 8
}

def resize_image(image, new_width=100, height_scale=0.55):
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width * height_scale)  # Adjust for font aspect ratio
    return image.resize((new_width, new_height))

def resize_image_for_braille(image, new_width=100, height_scale=1.0):
    width, height = image.size
    aspect_ratio = height / width
    target_width = max(2, new_width * 2)
    target_height = int(aspect_ratio * target_width * height_scale)
    target_height = max(4, target_height - (target_height % 4))
    if target_height <= 0:
        target_height = 4
    return image.resize((target_width, target_height))

def grayify(image):
    return image.convert("L")

def get_color_escape(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def normalize_theme_chars(theme, avoid_space=False):
    chars = THEMES.get(theme, THEMES["default"])
    if avoid_space:
        while chars and chars[-1] == " ":
            chars = chars[:-1]
    return chars

def _get_flat_pixels(image):
    if hasattr(image, "get_flattened_data"):
        return list(image.get_flattened_data())
    return list(image.getdata())

def _crop_to_braille_grid(image):
    width, height = image.size
    crop_width = width - (width % 2)
    crop_height = height - (height % 4)
    if crop_width != width or crop_height != height:
        image = image.crop((0, 0, crop_width, crop_height))
    return image

def pixels_to_braille(image, color_image=None, threshold=128):
    image = _crop_to_braille_grid(image)
    width, height = image.size
    pixels = _get_flat_pixels(image)

    if color_image is not None:
        color_image = _crop_to_braille_grid(color_image)
        color_pixels = _get_flat_pixels(color_image)
    else:
        color_pixels = None

    lines = []
    for y in range(0, height, 4):
        line_chars = []
        last_color = None
        for x in range(0, width, 2):
            mask = 0
            r_sum = g_sum = b_sum = 0
            for dy in range(4):
                for dx in range(2):
                    idx = (y + dy) * width + (x + dx)
                    if pixels[idx] < threshold:
                        mask |= BRAILLE_DOT_BITS[(dx, dy)]
                    if color_pixels is not None:
                        r, g, b = color_pixels[idx][:3]
                        r_sum += r
                        g_sum += g
                        b_sum += b

            char = chr(0x2800 + mask)
            if color_pixels is not None:
                r = r_sum // 8
                g = g_sum // 8
                b = b_sum // 8
                quantized_color = ((r // 16) * 16, (g // 16) * 16, (b // 16) * 16)
                if quantized_color != last_color:
                    line_chars.append(f"{get_color_escape(*quantized_color)}{char}")
                    last_color = quantized_color
                else:
                    line_chars.append(char)
            else:
                line_chars.append(char)
        if color_pixels is not None:
            lines.append("".join(line_chars) + Style.RESET_ALL)
        else:
            lines.append("".join(line_chars))
    return "\n".join(lines)

def pixels_to_braille_html(image, color_image=None, threshold=128):
    image = _crop_to_braille_grid(image)
    width, height = image.size
    pixels = _get_flat_pixels(image)

    if color_image is not None:
        color_image = _crop_to_braille_grid(color_image)
        color_pixels = _get_flat_pixels(color_image)
    else:
        color_pixels = None

    html_template = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ background-color: #000; color: #fff; font-family: 'Courier New', Courier, monospace; line-height: 1.0; font-size: 8px; }}
        pre {{ white-space: pre; }}
    </style>
</head>
<body>
    <pre>
{content}
    </pre>
</body>
</html>
"""

    lines = []
    for y in range(0, height, 4):
        line = ""
        for x in range(0, width, 2):
            mask = 0
            r_sum = g_sum = b_sum = 0
            for dy in range(4):
                for dx in range(2):
                    idx = (y + dy) * width + (x + dx)
                    if pixels[idx] < threshold:
                        mask |= BRAILLE_DOT_BITS[(dx, dy)]
                    if color_pixels is not None:
                        r, g, b = color_pixels[idx][:3]
                        r_sum += r
                        g_sum += g
                        b_sum += b

            char = chr(0x2800 + mask)
            if color_pixels is not None:
                r = r_sum // 8
                g = g_sum // 8
                b = b_sum // 8
                line += f'<span style="color: rgb({r},{g},{b})">{char}</span>'
            else:
                line += char
        lines.append(line)

    return html_template.format(content="\n".join(lines))

def apply_glitch_effects(lines, intensity=0.25, max_shift=10, slice_height=2, scramble_prob=0.03, rng=None):
    if intensity <= 0 or not lines:
        return lines

    rng = rng or random
    out = list(lines)
    slice_count = max(1, int(len(out) * intensity))

    for _ in range(slice_count):
        start = rng.randint(0, max(0, len(out) - 1))
        height = rng.randint(1, max(1, slice_height))
        shift = rng.randint(-max_shift, max_shift)
        end = min(len(out), start + height)
        for i in range(start, end):
            line = out[i]
            if shift > 0:
                line = (" " * shift) + line
            elif shift < 0:
                line = line[-shift:] if len(line) > -shift else ""
            out[i] = line

    if scramble_prob > 0:
        for i, line in enumerate(out):
            if "\033[" in line:
                continue
            if rng.random() < (scramble_prob * intensity):
                chars = list(line)
                rng.shuffle(chars)
                out[i] = "".join(chars)

    return out

class AudioLevelMeter:
    def __init__(self, device=None, samplerate=44100, blocksize=1024):
        self.available = False
        self.error = None
        self._level = 0.0
        self._lock = threading.Lock()
        self._stream = None
        try:
            import numpy as np
            import sounddevice as sd
        except Exception as exc:
            self.error = str(exc)
            return

        self._np = np
        self._sd = sd
        self.available = True
        self._device = device
        self._samplerate = samplerate
        self._blocksize = blocksize

    def start(self):
        if not self.available:
            return False

        def callback(indata, _frames, _time, _status):
            rms = float(self._np.sqrt(self._np.mean(indata ** 2)))
            level = min(1.0, rms * 10.0)
            with self._lock:
                self._level = (self._level * 0.8) + (level * 0.2)

        try:
            self._stream = self._sd.InputStream(
                device=self._device,
                channels=1,
                samplerate=self._samplerate,
                blocksize=self._blocksize,
                callback=callback,
            )
            self._stream.start()
            return True
        except Exception as exc:
            self.error = str(exc)
            self.available = False
            return False

    def get_level(self):
        with self._lock:
            return self._level

    def stop(self):
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

def pixels_to_ascii(image, theme="default", color_image=None, avoid_space=False):
    # Use get_flattened_data if available (Pillow 11+), else getdata
    pixels = _get_flat_pixels(image)
    
    width, height = image.size
    chars = normalize_theme_chars(theme, avoid_space=avoid_space)
    num_chars = len(chars)
    
    if color_image:
        color_pixels = _get_flat_pixels(color_image)
        
        lines = []
        last_color = None
        for y in range(height):
            line_chars = []
            for x in range(width):
                i = y * width + x
                # Get RGB values (ignoring alpha if present)
                r, g, b = color_pixels[i][:3]
                
                # Quantize colors to compress consecutive identical colors in the terminal
                quantized_color = ((r // 16) * 16, (g // 16) * 16, (b // 16) * 16)
                
                # Scale pixel value (0-255) to the number of available characters
                char_idx = int((pixels[i] / 255) * (num_chars - 1))
                char = chars[char_idx]
                
                if quantized_color != last_color:
                    line_chars.append(f"{get_color_escape(*quantized_color)}{char}")
                    last_color = quantized_color
                else:
                    line_chars.append(char)
            lines.append("".join(line_chars) + Style.RESET_ALL)
            last_color = None # Reset at the end of line because of Style.RESET_ALL
        return "\n".join(lines)
    else:
        # Scale pixel values to character set length
        ascii_chars = [chars[int((pixel / 255) * (num_chars - 1))] for pixel in pixels]
        ascii_image = "\n".join(["".join(ascii_chars[index:(index + width)]) for index in range(0, len(ascii_chars), width)])
        return ascii_image

def pixels_to_html(image, theme="default", color_image=None, avoid_space=False):
    pixels = _get_flat_pixels(image)
        
    width, height = image.size
    chars = normalize_theme_chars(theme, avoid_space=avoid_space)
    num_chars = len(chars)
    
    html_template = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ background-color: #000; color: #fff; font-family: 'Courier New', Courier, monospace; line-height: 0.6; font-size: 8px; }}
        pre {{ white-space: pre-wrap; word-wrap: break-word; }}
    </style>
</head>
<body>
    <pre>
{content}
    </pre>
</body>
</html>
"""
    
    if color_image:
        color_pixels = _get_flat_pixels(color_image)
    else:
        color_pixels = None
    lines = []
    
    for y in range(height):
        line = ""
        for x in range(width):
            i = y * width + x
            char_idx = int((pixels[i] / 255) * (num_chars - 1))
            char = chars[char_idx]
            
            # Escape HTML characters
            if char == "<": char = "&lt;"
            elif char == ">": char = "&gt;"
            elif char == "&": char = "&amp;"
            
            if color_pixels:
                rgb = color_pixels[i][:3]
                line += f'<span style="color: rgb({rgb[0]},{rgb[1]},{rgb[2]})">{char}</span>'
            else:
                line += char
        lines.append(line)
    
    return html_template.format(content="\n".join(lines))

def convert_image_to_ascii_image(
    image,
    new_width=100,
    height_scale=0.55,
    color=False,
    theme="default",
    contrast=1.0,
    brightness=1.0,
    edges=False,
    export_html=False,
    edge_blur=0.5,
    edge_contrast=3.0,
    edge_brightness=1.5,
    avoid_space=False,
    braille=False,
    braille_threshold=128
):
    # Apply enhancements
    if brightness != 1.0:
        image = ImageEnhance.Brightness(image).enhance(brightness)
    if contrast != 1.0:
        image = ImageEnhance.Contrast(image).enhance(contrast)

    # Store original for color mapping before potentially applying edges
    source_image = image

    # Apply edge detection if requested
    if edges:
        # Convert to grayscale first for cleaner edge detection
        edge_image = ImageOps.grayscale(image)
        # Smooth slightly to reduce noise
        if edge_blur and edge_blur > 0:
            edge_image = edge_image.filter(ImageFilter.GaussianBlur(radius=edge_blur))
        # Find edges
        edge_image = edge_image.filter(ImageFilter.FIND_EDGES)
        # Sharpen the edges
        edge_image = edge_image.filter(ImageFilter.SHARPEN)
        # Boost contrast significantly to isolate edges
        edge_image = ImageEnhance.Contrast(edge_image).enhance(edge_contrast)
        # Use a higher threshold/brightness to make edges "pop"
        edge_image = ImageEnhance.Brightness(edge_image).enhance(edge_brightness)
        image = edge_image

    if braille:
        resized_image = resize_image_for_braille(image, new_width, height_scale=height_scale)
        grayscale_image = grayify(resized_image)
    else:
        resized_image = resize_image(image, new_width, height_scale=height_scale)
        grayscale_image = grayify(resized_image)

    if export_html:
        if braille:
            color_data = resize_image_for_braille(source_image, new_width, height_scale=height_scale).convert("RGB") if color else None
            return pixels_to_braille_html(grayscale_image, color_image=color_data, threshold=braille_threshold)
        else:
            color_data = resize_image(source_image, new_width, height_scale=height_scale).convert("RGB") if color else None
            return pixels_to_html(grayscale_image, theme=theme, color_image=color_data, avoid_space=avoid_space)

    if braille:
        color_data = resize_image_for_braille(source_image, new_width, height_scale=height_scale).convert("RGB") if color else None
        return pixels_to_braille(grayscale_image, color_image=color_data, threshold=braille_threshold)
    if color:
        # Use the source image for color data
        color_data = resize_image(source_image, new_width, height_scale=height_scale).convert("RGB")
        return pixels_to_ascii(grayscale_image, theme=theme, color_image=color_data, avoid_space=avoid_space)
    else:
        return pixels_to_ascii(grayscale_image, theme=theme, avoid_space=avoid_space)

def convert_image_to_ascii(image_path, new_width=100, height_scale=0.55, color=False, theme="default", contrast=1.0, brightness=1.0, edges=False, export_html=False, avoid_space=False, braille=False, braille_threshold=128):
    try:
        image = Image.open(image_path)
        image = ImageOps.exif_transpose(image)
    except Exception as e:
        print(f"Unable to open image file {image_path}. Error: {e}")
        return

    return convert_image_to_ascii_image(
        image,
        new_width=new_width,
        height_scale=height_scale,
        color=color,
        theme=theme,
        contrast=contrast,
        brightness=brightness,
        edges=edges,
        export_html=export_html,
        avoid_space=avoid_space,
        braille=braille,
        braille_threshold=braille_threshold
    )

def render_ascii_frame(ascii_art, font):
    lines = ascii_art.splitlines()
    if not lines:
        return None

    max_len = max(len(line) for line in lines)
    char_box = font.getbbox("A")
    char_width = char_box[2] - char_box[0]
    char_height = char_box[3] - char_box[1]

    img_width = max_len * char_width
    img_height = len(lines) * char_height
    img = Image.new("RGB", (img_width, img_height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), "\n".join(lines), font=font, fill=(255, 255, 255))
    return img

def run_webcam_ascii(
    camera_index=0,
    new_width=100,
    height_scale=0.55,
    color=False,
    theme="default",
    contrast=1.0,
    brightness=1.0,
    edges=False,
    fps=15,
    clear_screen=True,
    use_alt_buffer=True,
    edge_blur=0.5,
    edge_contrast=3.0,
    edge_brightness=1.5,
    record_path=None,
    record_fps=None,
    record_seconds=None,
    avoid_space=True,
    braille=False,
    braille_threshold=128,
    glitch=False,
    glitch_intensity=0.25,
    glitch_slice_height=2,
    glitch_max_shift=10,
    glitch_scramble=0.03,
    audio_reactive=False,
    audio_gain=1.5,
    audio_device=None
):
    try:
        import cv2
    except Exception:
        print("OpenCV is required for webcam mode. Install it with: python -m pip install opencv-python")
        return

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Unable to access webcam at index {camera_index}.")
        return

    frame_delay = 1.0 / fps if fps and fps > 0 else 0
    if use_alt_buffer:
        sys.stdout.write("\033[?1049h")
    if clear_screen:
        sys.stdout.write("\033[H\033[2J")
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    writer = None
    record_start = time.time()
    record_font = ImageFont.load_default()
    if record_path:
        try:
            import imageio.v2 as imageio
            writer_fps = record_fps or fps or 15
            writer = imageio.get_writer(record_path, fps=writer_fps)
        except Exception as e:
            print(f"Unable to start recording: {e}")
            writer = None

    last_rows = 0
    last_cols = 0
    stop_requested = {"value": False}

    audio_meter = None
    if audio_reactive:
        audio_meter = AudioLevelMeter(device=audio_device)
        if not audio_meter.start():
            error_msg = audio_meter.error or "Unknown audio error"
            print(f"Audio reactivity disabled: {error_msg}")
            audio_meter = None
            audio_reactive = False

    def handle_sigint(_signum, _frame):
        stop_requested["value"] = True

    old_handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, handle_sigint)

    old_term = None
    try:
        old_term = termios.tcgetattr(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
    except Exception:
        old_term = None

    try:
        while True:
            if stop_requested["value"]:
                break

            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                key = sys.stdin.read(1)
                if key in ("q", "Q"):
                    break
                elif key in ("c", "C"):
                    color = not color

            start_time = time.time()
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            ascii_art = convert_image_to_ascii_image(
                pil_image,
                new_width=new_width,
                height_scale=height_scale,
                color=color,
                theme=theme,
                contrast=contrast,
                brightness=brightness,
                edges=edges,
                export_html=False,
                edge_blur=edge_blur,
                edge_contrast=edge_contrast,
                edge_brightness=edge_brightness,
                avoid_space=avoid_space,
                braille=braille,
                braille_threshold=braille_threshold
            )

            if glitch or audio_reactive:
                audio_level = audio_meter.get_level() if audio_meter else 0.0
                intensity = min(1.0, glitch_intensity + (audio_level * audio_gain))
                max_shift = int(glitch_max_shift + (audio_level * glitch_max_shift))
                lines = ascii_art.splitlines()
                lines = apply_glitch_effects(
                    lines,
                    intensity=intensity,
                    max_shift=max_shift,
                    slice_height=glitch_slice_height,
                    scramble_prob=glitch_scramble,
                )
                ascii_art = "\n".join(lines)

            sys.stdout.write("\033[H")

            lines = ascii_art.splitlines()
            # Append Clear to End of Line to avoid manual space padding which breaks with ANSI codes
            padded_lines = [line + "\033[K" for line in lines]
            
            if len(padded_lines) < last_rows:
                padded_lines.extend(["\033[K"] * (last_rows - len(padded_lines)))

            sys.stdout.write("\n".join(padded_lines))
            sys.stdout.write("\033[J")
            sys.stdout.flush()

            last_rows = len(padded_lines)

            if writer is not None:
                record_ascii = convert_image_to_ascii_image(
                    pil_image,
                    new_width=new_width,
                    height_scale=height_scale,
                    color=False,
                    theme=theme,
                    contrast=contrast,
                    brightness=brightness,
                    edges=edges,
                    export_html=False,
                    edge_blur=edge_blur,
                    edge_contrast=edge_contrast,
                    edge_brightness=edge_brightness,
                    avoid_space=avoid_space,
                    braille=braille,
                    braille_threshold=braille_threshold
                )
                frame_img = render_ascii_frame(record_ascii, record_font)
                if frame_img is not None:
                    writer.append_data(frame_img)

            if record_seconds and (time.time() - record_start) >= record_seconds:
                break

            elapsed = time.time() - start_time
            if frame_delay > 0 and elapsed < frame_delay:
                time.sleep(frame_delay - elapsed)
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        if writer is not None:
            writer.close()
        if audio_meter is not None:
            audio_meter.stop()
        if old_term is not None:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_term)
        signal.signal(signal.SIGINT, old_handler)
        sys.stdout.write("\033[?25h")
        if use_alt_buffer:
            sys.stdout.write("\033[?1049l")
        sys.stdout.write("\n")
        sys.stdout.flush()

def main():
    parser = argparse.ArgumentParser(description="Convert images to ASCII art")
    parser.add_argument("path", nargs="?", help="Path to the image file")
    parser.add_argument("--width", type=int, default=100, help="Width of the ASCII art (default: 100)")
    parser.add_argument("--height-scale", type=float, default=None, help="Height scaling factor for ASCII (default: 0.55, or 1.0 in braille mode)")
    parser.add_argument("--output", default="ascii_image.txt", help="Output file (default: ascii_image.txt)")
    parser.add_argument("--color", action="store_true", help="Enable colored output (terminal only)")
    parser.add_argument("--theme", choices=THEMES.keys(), default="default", help="Theme for ASCII characters")
    parser.add_argument("--braille", action="store_true", help="Enable high-resolution braille mode (2x4 pixel mapping)")
    parser.add_argument("--braille-threshold", type=int, default=128, help="Threshold for braille dots (0-255, default: 128)")
    parser.add_argument("--contrast", type=float, default=1.5, help="Contrast enhancement factor (default: 1.5)")
    parser.add_argument("--brightness", type=float, default=1.0, help="Brightness enhancement factor (default: 1.0)")
    parser.add_argument("--edges", action="store_true", help="Apply edge detection filter")
    parser.add_argument("--edge-blur", type=float, default=0.5, help="Edge detection blur radius (default: 0.5)")
    parser.add_argument("--edge-contrast", type=float, default=3.0, help="Edge detection contrast boost (default: 3.0)")
    parser.add_argument("--edge-brightness", type=float, default=1.5, help="Edge detection brightness boost (default: 1.5)")
    parser.add_argument("--html", action="store_true", help="Export to HTML file")
    parser.add_argument("--webcam", action="store_true", help="Use live webcam input")
    parser.add_argument("--camera", type=int, default=0, help="Webcam index (default: 0)")
    parser.add_argument("--fps", type=int, default=30, help="Target frames per second for webcam mode (default: 30)")
    parser.add_argument("--no-clear", action="store_true", help="Do not clear the terminal between frames")
    parser.add_argument("--no-alt-buffer", action="store_true", help="Disable alternate screen buffer in webcam mode")
    parser.add_argument("--record", help="Record webcam ASCII output to a file (GIF/MP4) using imageio")
    parser.add_argument("--record-fps", type=int, help="FPS for recorded output (defaults to --fps)")
    parser.add_argument("--record-seconds", type=float, help="Record duration in seconds (default: unlimited)")
    parser.add_argument("--glitch", action="store_true", help="Enable live glitch effects in webcam mode")
    parser.add_argument("--glitch-intensity", type=float, default=0.25, help="Glitch intensity (default: 0.25)")
    parser.add_argument("--glitch-slice-height", type=int, default=2, help="Max height of glitch slices (default: 2)")
    parser.add_argument("--glitch-max-shift", type=int, default=10, help="Max horizontal shift for glitches (default: 10)")
    parser.add_argument("--glitch-scramble", type=float, default=0.03, help="Chance to scramble a line (default: 0.03)")
    parser.add_argument("--audio-reactive", action="store_true", help="Make glitches react to microphone input")
    parser.add_argument("--audio-gain", type=float, default=1.5, help="Audio reactivity gain (default: 1.5)")
    parser.add_argument("--audio-device", type=int, help="Audio input device index for reactivity")
    
    args = parser.parse_args()

    height_scale = args.height_scale
    if height_scale is None:
        height_scale = 1.0 if args.braille else 0.55
    
    # If edges is enabled and theme is default, switch to lines theme for better results
    active_theme = args.theme
    if args.edges and active_theme == "default":
        active_theme = "lines"
    if args.braille:
        active_theme = "default"

    if args.webcam and args.html:
        parser.error("--html is not supported in --webcam mode")

    if args.webcam:
        run_webcam_ascii(
            camera_index=args.camera,
            new_width=args.width,
            height_scale=height_scale,
            color=args.color,
            theme=active_theme,
            contrast=args.contrast,
            brightness=args.brightness,
            edges=args.edges,
            fps=args.fps,
            clear_screen=not args.no_clear,
            use_alt_buffer=not args.no_alt_buffer,
            edge_blur=args.edge_blur,
            edge_contrast=args.edge_contrast,
            edge_brightness=args.edge_brightness,
            record_path=args.record,
            record_fps=args.record_fps,
            record_seconds=args.record_seconds,
            braille=args.braille,
            braille_threshold=args.braille_threshold,
            glitch=args.glitch,
            glitch_intensity=args.glitch_intensity,
            glitch_slice_height=args.glitch_slice_height,
            glitch_max_shift=args.glitch_max_shift,
            glitch_scramble=args.glitch_scramble,
            audio_reactive=args.audio_reactive,
            audio_gain=args.audio_gain,
            audio_device=args.audio_device
        )
        return

    if not args.path:
        parser.error("path is required unless --webcam is set")

    # If HTML export is requested and output is default, change extension
    output_path = args.output
    if args.html and output_path == "ascii_image.txt":
        output_path = "ascii_image.html"

    ascii_art = convert_image_to_ascii(
        args.path, 
        new_width=args.width,
        height_scale=height_scale,
        color=args.color, 
        theme=active_theme,
        contrast=args.contrast,
        brightness=args.brightness,
        edges=args.edges,
        export_html=args.html,
        braille=args.braille,
        braille_threshold=args.braille_threshold
    )
    
    if ascii_art:
        # Don't print full HTML to terminal unless it's very small
        if args.color and not args.html:
            print(ascii_art)
            
        with open(output_path, "w") as f:
            f.write(ascii_art)
            
        if args.html:
            print(f"Success! HTML ASCII art saved to {output_path}")
        elif args.color:
            print(f"\nSuccess! ASCII art saved to {output_path} (Note: color characters preserved in file)")
        else:
            print(f"Success! ASCII art saved to {output_path}")

if __name__ == "__main__":
    main()
