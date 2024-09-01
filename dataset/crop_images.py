import os
import numpy as np
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from tqdm import tqdm
from PIL import Image
from multiprocessing import Pool
import argparse

def get_args():
    parser = argparse.ArgumentParser(description="Parameters")

    parser.add_argument('--pdf_path', default="./SYNS_PDF", help="where synthesized .pdf files save")
    parser.add_argument('--save_path', default="./IMAGE", help="where the cropped image files save")
    
    args = parser.parse_args()
    return args


def process_pdf(pdf_file_path):
    margin=10
    threshold=5
    min_width=280
    min_height=60
    
    shard = int(os.path.basename(os.path.dirname(pdf_file_path)).replace("PDF", ""))
    image_dir = os.path.join(image_base_dir, f"IMAGE{shard}")
    if not os.path.exists(image_dir):
        os.makedirs(image_dir, exist_ok=True)

    try:
        reader = PdfReader(pdf_file_path)
        num_pages = len(reader.pages)

        if num_pages != 1:
            return

        images = convert_from_path(pdf_file_path)
        for image in images:
            gray_image = np.array(image.convert("L"))
            height, width = gray_image.shape

            non_white_pixels = np.argwhere(gray_image < 255)
            if non_white_pixels.size == 0:
                return

            y_top_left, x_top_left = non_white_pixels.min(axis=0)
            y_bottom_right, x_bottom_right = non_white_pixels.max(axis=0)

            if width - x_bottom_right <= threshold:
                print(f"Skipping {pdf_file_path} due to potential compilation issue.")
                return

            # 添加余量
            x_top_left = max(0, x_top_left - margin)
            y_top_left = max(0, y_top_left - margin)
            x_bottom_right = min(width, x_bottom_right + margin)
            y_bottom_right = min(height, y_bottom_right + margin)

            cropped_width = x_bottom_right - x_top_left
            cropped_height = y_bottom_right - y_top_left

            if cropped_width < min_width or cropped_height < min_height:
                print(f"Skipping {pdf_file_path} due to small cropped area ({cropped_width}x{cropped_height}).")
                return

            cropped_image = image.crop((x_top_left, y_top_left, x_bottom_right, y_bottom_right))

            base_name = os.path.splitext(os.path.basename(pdf_file_path))[0]
            image_file_path = os.path.join(image_dir, f"{base_name}.png")
            cropped_image.save(image_file_path)

    except Exception as e:
        print(f"Error processing {pdf_file_path}: {e}")

def crop_images(pdf_base_dir, image_base_dir):
    if not os.path.exists(image_base_dir):
        os.makedirs(image_base_dir, exist_ok=True)
    pdf_files = []
    for shard in range(1, len(os.listdir(pdf_base_dir))+1):
        pdf_dir = os.path.join(pdf_base_dir, f"PDF{shard}")
        for pdf_file in os.listdir(pdf_dir):
            if pdf_file.endswith(".pdf"):
                pdf_files.append(os.path.join(pdf_dir, pdf_file))

    with Pool() as pool:
        list(tqdm(pool.imap(process_pdf, pdf_files), total=len(pdf_files)))

if __name__ == "__main__":
    args = get_args()

    pdf_base_dir = args.pdf_path
    image_base_dir = args.save_path
    
    crop_images(pdf_base_dir, image_base_dir)


