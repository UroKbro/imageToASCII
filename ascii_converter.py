from PIL import Image, ImageOps
import argparse

ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]
def resize_image(image, new_width=100):
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width * 0.55)  # Adjust for font aspect ratio
    return image.resize((new_width, new_height))

def grayify(image):
    return image.convert("L")

def pixels_to_ascii(image):
    pixels = image.get_flattened_data()
    characters = "".join([ASCII_CHARS[pixel // 25] for pixel in pixels])
    return characters

def convert_image_to_ascii(image_path, new_width=100):
    try:
        image = Image.open(image_path)
        image = ImageOps.exif_transpose(image)
    except Exception as e:
        print(f"Unable to open image file {image_path}. Error: {e}")
        return

    new_image_data = pixels_to_ascii(grayify(resize_image(image, new_width)))
    # Format the string into lines matching the new width
    pixel_count = len(new_image_data)
    ascii_image = "\n".join([new_image_data[index:(index + new_width)] for index in range(0, pixel_count, new_width)])

    return ascii_image

def main():
    parser = argparse.ArgumentParser(description="Convert images to ASCII art")
    parser.add_argument("path", help="Path to the image file")
    parser.add_argument("--width", type=int, default=100, help="Width of the ASCII art (default: 100)")
    parser.add_argument("--output", default="ascii_image.txt", help="Output file (default: ascii_image.txt)")
    
    args = parser.parse_args()
    
    ascii_art = convert_image_to_ascii(args.path, new_width=args.width)
    
    if ascii_art:
        with open(args.output, "w") as f:
            f.write(ascii_art)
        print(f"Success! ASCII art saved to {args.output}")

if __name__ == "__main__":
    main()
    
