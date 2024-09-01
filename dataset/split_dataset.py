import os
import random
from PIL import Image
from tqdm import tqdm
import argparse

def get_args():
    parser = argparse.ArgumentParser(description="Parameters")

    parser.add_argument('--save_imgs', default="./data/images", help="image paths")
    parser.add_argument('--save_labels', default="./data/labels", help="label paths")
    parser.add_argument('--tex_path', default="./SYNS_TEX", help="where the .tex files save")
    parser.add_argument('--img_path', default="./IMAGE", help="where the .png files save")
    
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = get_args()
    random.seed(42)
    
    all_img_paths = []
    all_label_paths = []
    tex_base_dir = args.tex_path
    img_base_dir = args.img_path

    for i in tqdm(range(1, len(os.listdir(tex_base_dir))+1)):
        img_dir = os.path.join(img_base_dir, f"IMAGE{i}")
        imgs = [os.path.join(img_dir, filename) for filename in os.listdir(img_dir)]
        texes = [img.replace(img_base_dir, tex_base_dir).replace("IMAGE", "TEX").replace(".png", ".tex") for img in imgs]

        valid_imgs = []
        valid_texes = []
        for img, tex in tqdm(list(zip(imgs, texes))):
            try:
                with Image.open(img) as im:
                    im.verify() 
                valid_imgs.append(img)
                valid_texes.append(tex)
            except (IOError, SyntaxError):
                print(f"cannot open: {img}, correspond {tex} will be also ignored")
                os.remove(img)
                if os.path.exists(tex):
                    os.remove(tex)

        all_img_paths.extend(valid_imgs)
        all_label_paths.extend(valid_texes)

    all_img_paths = sorted(all_img_paths)
    all_label_paths = sorted(all_label_paths)

    combined = list(zip(all_img_paths, all_label_paths))
    random.shuffle(combined)
    all_img_paths[:], all_label_paths[:] = zip(*combined)

    total_len = len(all_img_paths)
    train_split_idx = int(0.8 * total_len)
    val_split_idx = int(0.9 * total_len)

    train_img_paths = all_img_paths[:train_split_idx]
    train_label_paths = all_label_paths[:train_split_idx]
    val_img_paths = all_img_paths[train_split_idx:val_split_idx]
    val_label_paths = all_label_paths[train_split_idx:val_split_idx]
    test_img_paths = all_img_paths[val_split_idx:]
    test_label_paths = all_label_paths[val_split_idx:]

    img_save_dir = args.save_imgs
    tex_save_dir = args.save_labels
    os.makedirs(img_save_dir, exist_ok=True)
    os.makedirs(tex_save_dir, exist_ok=True)

    with open(os.path.join(img_save_dir, "train_images.txt"), "w") as train_img_file, \
        open(os.path.join(tex_save_dir, "train_labels.txt"), "w") as train_label_file, \
        open(os.path.join(img_save_dir, "val_images.txt"), "w") as val_img_file, \
        open(os.path.join(tex_save_dir, "val_labels.txt"), "w") as val_label_file, \
        open(os.path.join(img_save_dir, "test_images.txt"), "w") as test_img_file, \
        open(os.path.join(tex_save_dir, "test_labels.txt"), "w") as test_label_file:

        for path in train_img_paths:
            train_img_file.write(path + "\n")
        for path in train_label_paths:
            train_label_file.write(path + "\n")
        for path in val_img_paths:
            val_img_file.write(path + "\n")
        for path in val_label_paths:
            val_label_file.write(path + "\n")
        for path in test_img_paths:
            test_img_file.write(path + "\n")
        for path in test_label_paths:
            test_label_file.write(path + "\n")

    print("All data ready!")
