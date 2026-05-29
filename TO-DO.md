# TO-DO: Image to ASCII Improvements

Here are some ideas to level up the ASCII converter:

### 1. Command Line Interface (CLI)
Instead of changing the code every time, use `argparse` to pass arguments:
`python ascii_converter.py my_image.jpg --width 120 --output art.txt`

### 2. Color Support
Use `colorama` or ANSI escape codes to make the ASCII characters match the original colors of the image.

### 3. Multiple Character Sets
Add "themes" for different looks:
*   **Simple:** `["#", "S", "+", ".", " "]`
*   **Complex:** A 70-character string for smoother gradients.
*   **Binary:** Just `0` and `1` for a "Matrix" look.

### 4. Contrast & Brightness Control
Automatically boost contrast before conversion to make the final art "pop" more.

### 5. Inversion Flag
Add an `--invert` option to swap character mapping for light vs. dark terminal backgrounds.

### 6. HTML Export
Generate an `.html` file to support full color and fixed-width fonts for easier sharing.

### 7. Edge Detection
Use filters (like Sobel or Canny) to create "line drawing" versions of the ASCII art.

### 8. Real-time Webcam
Use `OpenCV` to capture a live webcam feed and display a live ASCII video in the terminal.
