import logic.fileio.file_verifier as image_handler
from logic.image_logic import image_to_redstone_lamps, img_to_blocks
import PIL
from PIL import Image
import io
import math


# Loads the image for displaying in the preview
def load_image_for_display(filepath: str, size: tuple[int, int]) -> bool | tuple[list[int], io.BytesIO] | None:
    if image_handler.check_file_exists(filepath):
        try:
            img = Image.open(filepath)
        except (FileNotFoundError, PIL.UnidentifiedImageError):
            return False

        width = img.width
        height = img.height
        img_size = [432, 240]

        img_size[0] = min(432, math.floor(size[0] / 2))
        img_size[1] = min(240, math.floor(size[1] / 2))

        img.thumbnail((img_size[0], img_size[1]), Image.Resampling.LANCZOS)
        b_io = io.BytesIO()
        img.save(b_io, format="PNG")
        return [width, height], b_io
    return None
    pass


# Converts the loaded image, to put it to preview
def load_image_for_preview(
        image_bytes: io.BytesIO, manipulation: str, brightness: int, blocklist: list, mode: str, side
):
    img = Image.open(image_bytes)
    img.thumbnail((img.width // 2, img.height // 2))
    out_img = None
    if "Lamps" in manipulation:
        for value in image_to_redstone_lamps.img_to_redstone_lamps(img, brightness):
            if isinstance(value, Image.Image):
                out_img = value
        out_img.thumbnail((350, 240))
        # Saving the image in a bytes format, so it can be used without storing as a file
        b_io = io.BytesIO()
        out_img.save(b_io, format="PNG")
        return b_io
    elif "Any" in manipulation:
        img = img.convert("RGBA")
        img.thumbnail((img.width // 2, img.height // 2))
        for value in img_to_blocks.img_to_blocks(img, side, blocklist, mode):
            if isinstance(value, Image.Image):
                out_img = value
        out_img.thumbnail((350, 240))
        b_io = io.BytesIO()
        out_img.save(b_io, format="PNG")
        return b_io
    return image_bytes
