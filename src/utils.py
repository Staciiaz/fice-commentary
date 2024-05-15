import cv2
import numpy as np


def put_text_on_image(
        image: np.ndarray[np.uint8], text: str, x: int, y: int, font_face: int = cv2.FONT_HERSHEY_SIMPLEX,
        font_scale: int = 1, text_thickness: int = 2) -> None:
    (text_width, text_height), baseline = cv2.getTextSize(text, font_face, font_scale, text_thickness)
    image_height, image_width, _ = image.shape
    text_x = (image_width - text_width) // 2 + (x - 480)
    text_y = (image_height + text_height) // 2 + (y - 320)
    cv2.putText(image, text, (text_x, text_y), font_face, font_scale, (255, 255, 255), text_thickness)
