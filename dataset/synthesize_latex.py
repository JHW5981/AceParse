from process_latex import get_latex, extract_all
from tqdm import tqdm
import os
import json
import uuid
import random
import argparse

def merge_dicts(dict1, dict2):
    return {key: dict1[key] + dict2[key] for key in dict1.keys() & dict2.keys()}

def generate_uuid_filename(extension=''):
    # generate uuid
    unique_filename = str(uuid.uuid4())
    return unique_filename + extension

def extract_elements(tex_path, save_path="./dataset/data.json"):
    
    data_all = {
        "algorithms": [],
        "formulas": [],
        "tables": [],
        "items": [],
        "elses": [],
        "sentences": []
    }

    texes = os.listdir(tex_path)
    for tex in tqdm(texes):
        tex_path = os.path.join(tex_path, tex)
        try:
            tex, command_replacements = get_latex(tex_path)
        except:
            continue

        data = extract_all(tex, command_replacements)
        data_all = merge_dicts(data_all, data)

    print("algorithm:", len(data_all["algorithms"]))
    print("formula_list:", len(data_all["formulas"]))
    print("table_list:", len(data_all["tables"]))
    print("item_list:", len(data_all["items"]))
    print("sentence_list:", len(data_all["sentences"]))    
    print("else_list:", len(data_all["elses"]))    

    # write to json
    with open(save_path, 'w', encoding='utf-8') as json_file:
        json.dump(data_all, json_file, ensure_ascii=False, indent=4)
    return data_all

def synthesize_tex(data_all, save_file="./SYNS_TEX", length_options=[1400, 1600, 1800], total_files=10, files_per_shard=10):
    lists_with_probabilities = {
        "algorithm_list": (data_all["algorithms"], 0.4),
        "formula_list": (data_all["formulas"], 0.4),
        "table_list": (data_all["tables"], 0.4),
        "item_list": (data_all["items"], 0.4),
        "sentence_list": (data_all["sentences"], 0.8),
    }

    for i in tqdm(range(total_files)):
        shard_number = i // files_per_shard + 1
        shard_dir = f"{save_file}/TEX{shard_number}"
        if not os.path.exists(shard_dir):
            os.makedirs(shard_dir)
        
        max_length = random.choice(length_options)

        tex_content = r"""\documentclass{article}
\usepackage{amsmath}
\usepackage{xcolor}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{algorithm}
\usepackage{algorithmic}

\begin{document}
\pagenumbering{gobble}

"""

        init_length = len(tex_content)
        selected_element_list = []

        current_length = init_length
        # to make the generated text as close as possible to the specified length
        while current_length < max_length:
            for key, (items, probability) in lists_with_probabilities.items():
                if random.random() < probability:
                    try:
                        selected_element = random.choice(items)
                    except IndexError:
                        continue
                    if current_length + len(selected_element) + 1 < max_length:
                        tex_content += selected_element + "\n\n"
                        selected_element_list.append((key, selected_element))
                        current_length += len(selected_element) + 1
                    else:
                        current_length += len(selected_element) + 1
                        break 
            if current_length >= max_length:
                break
            
        if len(tex_content) - init_length <=10:
            continue      
          
        tex_content += r"""
\end{document}"""        
        
        file_name = generate_uuid_filename(".tex")
        file_path = os.path.join(shard_dir, file_name)

        with open(file_path, "w") as f:
            f.write(tex_content)

def get_args():
    parser = argparse.ArgumentParser(description="Parameters")

    parser.add_argument('--tex_path', default="./TEX", help="where the .tex files save")
    parser.add_argument('--save_file', default="./SYNS_TEX", help="where synthesized .tex files save")
    parser.add_argument('--length_options', default=[1400, 1600, 1800], type=lambda s: [int(n) for n in s.split(',')], required=True, help='list of text lengths')
    parser.add_argument('--total_files', default=10, type=int, help="number of synthesized files")
    parser.add_argument('--files_per_shard', default=10, type=int, help="number of synthesized files per shard, to avoid having too many files in a single folder")
    
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = get_args()
    # extract elements
    data_all = extract_elements(args.tex_path)
    # synthesize data
    synthesize_tex(data_all, args.save_file, args.length_options, args.total_files, args.files_per_shard)



