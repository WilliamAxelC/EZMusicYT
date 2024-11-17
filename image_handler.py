from PIL import Image
import error_handler

def crop_to_square(image_path):
    try:
        image = Image.open(image_path)
        width, height = image.size
        size = min(width, height)
        left = (width - size) / 2
        top = (height - size) / 2
        right = (width + size) / 2
        bottom = (height + size) / 2
        cropped_image = image.crop((left, top, right, bottom))
        cropped_image.save(image_path)
        return cropped_image
    except Exception as e:
        error_handler.handle_error(f"Failed to crop image: {e}")
        return None
