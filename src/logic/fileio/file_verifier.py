import os.path


# Checks if a file exists
def check_file_exists(filepath: str) -> bool:
    return os.path.isfile(filepath)


def check_if_file_image(filepath: str) -> bool:
    list_of_image_extensions = (
        ".png",
        ".jpg",
        ".jpeg",
    )
    if filepath.endswith(list_of_image_extensions):
        return True
    return False
