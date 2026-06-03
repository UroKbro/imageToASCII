from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import argparse
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

def resize_image(image, new_width=100):
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width * 0.55)  # Adjust for font aspect ratio
    return image.resize((new_width, new_height))

def grayify(image):
    return image.convert("L")

def get_color_escape(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def pixels_to_ascii(image, theme="default", color_image=None):
    # Use get_flattened_data if available (Pillow 11+), else getdata
    if hasattr(image, 'get_flattened_data'):
        pixels = list(image.get_flattened_data())
    else:
        pixels = list(image.getdata())
    
    width, height = image.size
    chars = THEMES.get(theme, THEMES["default"])
    num_chars = len(chars)
    
    if color_image:
        if hasattr(color_image, 'get_flattened_data'):
            color_pixels = list(color_image.get_flattened_data())
        else:
            color_pixels = list(color_image.getdata())
        
        lines = []
        for y in range(height):
            line = ""
            for x in range(width):
                i = y * width + x
                # Get RGB values (ignoring alpha if present)
                rgb = color_pixels[i][:3]
                # Scale pixel value (0-255) to the number of available characters
                char_idx = int((pixels[i] / 255) * (num_chars - 1))
                char = chars[char_idx]
                line += f"{get_color_escape(*rgb)}{char}"
            lines.append(line + Style.RESET_ALL)
        return "\n".join(lines)
    else:
        # Scale pixel values to character set length
        ascii_chars = [chars[int((pixel / 255) * (num_chars - 1))] for pixel in pixels]
        ascii_image = "\n".join(["".join(ascii_chars[index:(index + width)]) for index in range(0, len(ascii_chars), width)])
        return ascii_image

def pixels_to_html(image, theme="default", color_image=None):
    if hasattr(image, 'get_flattened_data'):
        pixels = list(image.get_flattened_data())
    else:
        pixels = list(image.getdata())
        
    width, height = image.size
    chars = THEMES.get(theme, THEMES["default"])
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
        if hasattr(color_image, 'get_flattened_data'):
            color_pixels = list(color_image.get_flattened_data())
        else:
            color_pixels = list(color_image.getdata())
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

def convert_image_to_ascii(image_path, new_width=100, color=False, theme="default", contrast=1.0, brightness=1.0, edges=False, export_html=False):
    try:
        image = Image.open(image_path)
        image = ImageOps.exif_transpose(image)
    except Exception as e:
        print(f"Unable to open image file {image_path}. Error: {e}")
        return

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
        edge_image = edge_image.filter(ImageFilter.GaussianBlur(radius=0.5))
        # Find edges
        edge_image = edge_image.filter(ImageFilter.FIND_EDGES)
        # Sharpen the edges
        edge_image = edge_image.filter(ImageFilter.SHARPEN)
        # Boost contrast significantly to isolate edges
        edge_image = ImageEnhance.Contrast(edge_image).enhance(3.0)
        # Use a higher threshold/brightness to make edges "pop"
        edge_image = ImageEnhance.Brightness(edge_image).enhance(1.5)
        image = edge_image

    resized_image = resize_image(image, new_width)
    grayscale_image = grayify(resized_image)
    
    if export_html:
        color_data = resize_image(source_image, new_width).convert("RGB") if color else None
        return pixels_to_html(grayscale_image, theme=theme, color_image=color_data)
    
    if color:
        # Use the source image for color data
        color_data = resize_image(source_image, new_width).convert("RGB")
        return pixels_to_ascii(grayscale_image, theme=theme, color_image=color_data)
    else:
        return pixels_to_ascii(grayscale_image, theme=theme)

def main():
    parser = argparse.ArgumentParser(description="Convert images to ASCII art")
    parser.add_argument("path", help="Path to the image file")
    parser.add_argument("--width", type=int, default=100, help="Width of the ASCII art (default: 100)")
    parser.add_argument("--output", default="ascii_image.txt", help="Output file (default: ascii_image.txt)")
    parser.add_argument("--color", action="store_true", help="Enable colored output (terminal only)")
    parser.add_argument("--theme", choices=THEMES.keys(), default="default", help="Theme for ASCII characters")
    parser.add_argument("--contrast", type=float, default=1.5, help="Contrast enhancement factor (default: 1.5)")
    parser.add_argument("--brightness", type=float, default=1.0, help="Brightness enhancement factor (default: 1.0)")
    parser.add_argument("--edges", action="store_true", help="Apply edge detection filter")
    parser.add_argument("--html", action="store_true", help="Export to HTML file")
    
    args = parser.parse_args()
    
    # If edges is enabled and theme is default, switch to lines theme for better results
    active_theme = args.theme
    if args.edges and active_theme == "default":
        active_theme = "lines"

    # If HTML export is requested and output is default, change extension
    output_path = args.output
    if args.html and output_path == "ascii_image.txt":
        output_path = "ascii_image.html"

    ascii_art = convert_image_to_ascii(
        args.path, 
        new_width=args.width, 
        color=args.color, 
        theme=active_theme,
        contrast=args.contrast,
        brightness=args.brightness,
        edges=args.edges,
        export_html=args.html
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
