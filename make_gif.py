import os
import cv2
from PIL import Image

def create_gif_with_numbers(image_folder="images", output_filename="output.gif", duration=100, loop=0):
    """
    Create an animated GIF from all PNG images in the specified folder,
    adding a running number to each frame in the top-left corner.
    
    :param image_folder: Directory containing the images.
    :param output_filename: Name of the output GIF file.
    :param duration: Duration of each frame in milliseconds.
    :param loop: Number of loops (0 = infinite).
    """
    images = []

    # Get all PNG files and sort them numerically
    file_list = sorted(
        [f for f in os.listdir(image_folder) if f.endswith(".png")],
        key=lambda x: int(x.split('.')[0])  # Sorting numerically
    )

    if not file_list:
        print("No PNG images found in the directory.")
        return

    for idx, filename in enumerate(file_list):
        img_path = os.path.join(image_folder, filename)

        # Read image using OpenCV
        img = cv2.imread(img_path)

        # Define text properties
        text = f"Iter {idx //3}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        color = (255, 255, 255)  # White text
        thickness = 2

        # Get text size
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = 10
        text_y = text_size[1] + 10  # Add padding from top

        # Draw black rectangle behind text for readability
        cv2.rectangle(img, (text_x - 5, text_y - text_size[1] - 5),
                      (text_x + text_size[0] + 5, text_y + 5), (0, 0, 0), -1)

        # Put text on image
        cv2.putText(img, text, (text_x, text_y), font, font_scale, color, thickness)

        # Convert to RGB for Pillow
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        images.append(Image.fromarray(img_rgb))

    # Save as GIF
    images[0].save(
        output_filename,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=loop
    )
    print(f"GIF saved as {output_filename}")

# Run the function
create_gif_with_numbers()

