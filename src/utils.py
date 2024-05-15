import cv2
import numpy as np
from typing_extensions import List, Tuple


def split_texts_to_lines(text: str, max_width: int, font: int, font_scale: float, thickness: int) -> List[str]:
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        if cv2.getTextSize(current_line + word, font, font_scale, thickness)[0][0] <= max_width:
            current_line += word + ' '
        else:
            lines.append(current_line)
            current_line = word + ' '
    lines.append(current_line)  # add the last line
    return lines


def calculate_total_text_size(lines: List[str], font: int, font_scale: float, thickness: int) -> Tuple[int, int]:
    # Calculate total text block height
    total_text_height = 0
    max_line_width = 0
    line_heights = []
    line_widths = []
    for line in lines:
        (line_width, line_height), _ = cv2.getTextSize(line, font, font_scale, thickness)
        line_heights.append(line_height)
        line_widths.append(line_width)
        total_text_height += int(line_height * 1.5)  # line height with spacing
        if line_width > max_line_width:
            max_line_width = line_width
    return total_text_height, max_line_width


def draw_background(image: np.ndarray, x: int, y: int, width: int, height: int, color: Tuple[int, int, int], padding: int):
    img_height, img_width = image.shape[:2]
    # Calculate the dimensions of the background box
    background_width = width + 2 * padding
    background_height = height + padding  # only one padding at the top
    # Calculate starting coordinates for the background box
    bg_x = (img_width - background_width) // 2 + (x - 480)
    bg_y = (img_height - background_height) // 2 + (y - 320)
    # Draw the background box
    cv2.rectangle(image, (bg_x, bg_y), (bg_x + background_width, bg_y + background_height), color, cv2.FILLED)


def put_multiline_text(image: np.ndarray, lines: List[str], pos_x: int, pos_y: int, font: int, font_scale: float, thickness: int, color: Tuple[int, int, int], line_type: int):
    img_height, img_width = image.shape[:2]
    total_text_height, _ = calculate_total_text_size(lines, font, font_scale, thickness)
    # Calculate starting y-coordinate
    y0 = (img_height - total_text_height) // 2
    # Draw each line centered
    y = y0
    for i, line in enumerate(lines):
        (line_width, line_height), _ = cv2.getTextSize(line, font, font_scale, thickness)
        x = (img_width - line_width) // 2
        y += line_height
        text_x = x + (pos_x - 480)
        text_y = y + (pos_y - 320)
        cv2.putText(image, line, (text_x, text_y), font, font_scale, color, thickness, line_type)
        y += int(line_height * 0.5)  # adjust the line height for spacing


def put_text_on_image(image: np.ndarray, text: str, x: int, y: int):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    thickness = 2
    text_color = (255, 255, 255)
    line_type = cv2.LINE_AA
    max_width = 800
    background_color = (0, 0, 0)
    padding = 10
    lines = split_texts_to_lines(text, max_width, font, font_scale, thickness)
    total_text_height, max_line_width = calculate_total_text_size(lines, font, font_scale, thickness)
    draw_background(image, x, y, max_line_width, total_text_height, background_color, padding)
    put_multiline_text(image, lines, x, y, font, font_scale, thickness, text_color, line_type)
