import os
import base64


def image_to_url(image_path: str) -> base64:
    """Translate image file to data url(base64) to input image to llm model.

    Args:
        image_path (str): Path to image

    Returns:
        str: data url
    """

    res = ""

    if not image_path or not os.path.exists(image_path):
        return res
    file_type = os.path.splitext(image_path)[1].lower().lstrip(".")
    mime = "image/jpeg" if file_type in ["jpg", "jpeg"] else f"image/{file_type}"

    with open(image_path, "rb") as fh:
        b64 = base64.b64encode(fh.read().decode("utf-8"))

    res = f"data:{mime};base64,{b64}"

    return res
