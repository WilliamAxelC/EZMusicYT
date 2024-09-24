import urllib
from PIL import Image

def download_image(image_url, save_path):
    try:
        urllib.request.urlretrieve(image_url, save_path)
        print(f"Image downloaded to {save_path}")
    except Exception as e:
        print(f"Failed to download image: {e}")

def crop_to_square(image_path):
    try:
        image = Image.open(image_path)
        width, height = image.size
        size = min(width, height)
        left = (width - size) / 2
        top = (height - size) / 2
        right = (width + size) / 2
        bottom = (height + size) / 2
        return image.crop((left, top, right, bottom))
    except Exception as e:
        print(f"Failed to crop image: {e}")
        return Image.open(image_path)
