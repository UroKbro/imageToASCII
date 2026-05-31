from PIL import Image, ImageOps
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
    "blocks": ["█", "▓", "▒", "░", " "]
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
    pixels = list(image.getdata())
    width, height = image.size
    chars = THEMES.get(theme, THEMES["default"])
    num_chars = len(chars)
    
    if color_image:
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

def convert_image_to_ascii(image_path, new_width=100, color=False, theme="default"):
    try:
        image = Image.open(image_path)
        image = ImageOps.exif_transpose(image)
    except Exception as e:
        print(f"Unable to open image file {image_path}. Error: {e}")
        return

    resized_image = resize_image(image, new_width)
    grayscale_image = grayify(resized_image)
    
    if color:
        # We need the original color image in the same resolution
        return pixels_to_ascii(grayscale_image, theme=theme, color_image=resized_image.convert("RGB"))
    else:
        return pixels_to_ascii(grayscale_image, theme=theme)

def main():
    parser = argparse.ArgumentParser(description="Convert images to ASCII art")
    parser.add_argument("path", help="Path to the image file")
    parser.add_argument("--width", type=int, default=100, help="Width of the ASCII art (default: 100)")
    parser.add_argument("--output", default="ascii_image.txt", help="Output file (default: ascii_image.txt)")
    parser.add_argument("--color", action="store_true", help="Enable colored output (terminal only)")
    parser.add_argument("--theme", choices=THEMES.keys(), default="default", help="Theme for ASCII characters")
    
    args = parser.parse_args()
    
    ascii_art = convert_image_to_ascii(args.path, new_width=args.width, color=args.color, theme=args.theme)
    
    if ascii_art:
        # Always output to terminal if color is requested
        if args.color:
            print(ascii_art)
            
        with open(args.output, "w") as f:
            f.write(ascii_art)
            
        if args.color:
            print(f"\nSuccess! ASCII art saved to {args.output} (Note: color characters preserved in file)")
        else:
            print(f"Success! ASCII art saved to {args.output}")

if __name__ == "__main__":
    main()
