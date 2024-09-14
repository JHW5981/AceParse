<p align="center">
  <img src="./assets/logo.png" alt="sadpd-logo" width="15%">
  <h3 align="center">
    AceParse: A Comprehensive Dataset with Diverse Structured Texts for Academic Literature Parsing
  </h3>
  <p align="center">
    <a href=''><img src='https://img.shields.io/badge/Paper-ArXiv-C71585'></a> 
    <a href="https://github.com/JHW5981/AceParse/blob/master/LICENSE"><img alt="GitHub" src="https://img.shields.io/github/license/JHW5981/AceParse?color=blue"></a>
    <a href='https://huggingface.co/jihuawei/AcaParser'><img src='https://img.shields.io/badge/%F0%9F%A4%97%20Hugging Face-AceParser-red'></a>  
    <a href='https://huggingface.co/datasets/jihuawei/AceParse'><img src='https://img.shields.io/badge/Dataset-AceParse-4169E1'></img></a>
  </p>
</p>

This is the official repository for AceParse, a comprehensive dataset with diverse structured texts for academic literature parsing.

Project page: https://github.com/JHW5981/AceParse/

## Overview
AceParse includes various types of structured text, such as formulas, tables, algorithms, lists, and sentences embedded with mathematical expressions, among others. We provide examples of several dataset samples to give you a better understanding of our dataset.

<img src="./assets/samples.png" alt="samples" width="1000"/>

Above, we have provided document images in AceParse that contain different types of structured text. The parsing results of the aforementioned images are marked using LaTeX. For detailed examples, refer to `./dataset/samples`.

## Data Engine
The following figure illustrates the construction process of our dataset.

<img src="./assets/data_engine.png" alt="data_engine" width="1000"/>

To generate a dataset using our data engine, you need to run

```
python ./dataset/download_source.py --request_num 2 --arxiv_ids ./dataset/arxiv_ids.txt --source_path ./dataset/downloads --tex_path ./dataset/TEX
```

After the code execution is completed, we will obtain a TEX folder under the `./dataset` directory, which contains the LaTeX source code of academic literature. Then, run

```
python ./dataset/synthesize_latex.py --tex_path ./dataset/TEX --save_file ./dataset/SYNS_TEX --length_options 1400,1600,1800 --total_files 10 --files_per_shard 10
```

After this, we obtain the synthesized LaTeX code, which is located in the `./dataset/SYNS_TEX` folder. Then, run

```
bash ./dataset/generate_pdfs.sh ./dataset/SYNS_TEX ./dataset/SYNS_PDF 
```

After this, we obtain the compiled PDFs, which are located in the `./dataset/SYNS_PDF` folder. Then, run

```
python ./dataset/crop_images.py --pdf_path ./dataset/SYNS_PDF --save_path ./dataset/IMAGE 
```

We obtain the final document images, which are located in the `./dataset/IMAGE` folder.

Run

```
python ./dataset/split_dataset.py --save_imgs ./dataset/data/images --save_labels ./dataset/data/labels --tex_path ./dataset/SYNS_TEX --img_path ./dataset/IMAGE
```

This will generate the paths for the training, validation, and test set images, along with the corresponding parsed text. The generated path files are located in the `./dataset/data` directory.

Finally, the organization of our dataset is as follows:

```
dataset/
├── downloads/ # original source files
├── TEX/ # .tex extracted from source
├── SYNS_TEX/ # synthesized .tex files
├── SYNS_PDF/ # pdfs after compiling synthesized .tex
├── IMAGE/ # .png images cropped from synthesized .pdf 
├── data/
│   ├── images/ # image paths
│   └── labels/ # tex label paths
└── samples # samples of AceParse
```

## Example of Loading and Displaying the Data

We have uploaded the AceParse dataset to [huggingface🤗](https://huggingface.co/datasets/jihuawei/AceParse). You can directly import our dataset using the following code:

```
from datasets import load_dataset
from PIL import Image
import io
import numpy as np
import matplotlib.pyplot as plt

ds = load_dataset("jihuawei/AceParse", split='train')

# convert binary image to PIL image
image = Image.open(io.BytesIO(ds[0]['image']))

# get numpy image
image_array = np.array(image)

# label
label = ds[0]['label']

# show picture
plt.imshow(image_array)
plt.axis('off') 
plt.show()

# print label
print("Label:", label)
```

## Training
If you want to train your AceParser, you can run it directly:

```
python ./model/train_aceparser.py --train_img_paths ./dataset/data/images/train_images.txt --train_label_paths ./dataset/data/labels/train_labels.txt --eval_img_paths ./dataset/data/images/val_images.txt --output_dir ./model/weights
```

## Inference
We have uploaded the model to [huggingface🤗](https://huggingface.co/datasets/jihuawei/AceParser). You can use the following code for inferring.

```
from transformers import AutoProcessor, AutoModelForCausalLM
from PIL import Image
import torch

# model
model_id = "jihuawei/AcaParser"
acaparser_model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True).eval().to('cuda:1')
acaparser_processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)  
def acaparser(image_path):
    image = Image.open(image_path)
    task_prompt = "<OCR>"
    instruction = 'What is the text in the image?'
    pixel_values = acaparser_processor.image_processor(image)['pixel_values'][0]
    pixel_values = torch.tensor(pixel_values).unsqueeze(0)
    input_ids = acaparser_processor.tokenizer(
        instruction,
        return_tensors='pt',
        max_length=1024,
        truncation=True
    )['input_ids'] 
    generated_ids = acaparser_model.generate(
      input_ids=input_ids.to('cuda:1'),
      pixel_values=pixel_values.to('cuda:1'),
      max_new_tokens=1024,
      early_stopping=False,
      do_sample=False,
      num_beams=3,
    )
    generated_text = acaparser_processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
    parsed_answer = acaparser_processor.post_process_generation(
        generated_text, 
        task=task_prompt, 
        image_size=(image.width, image.height)
    )
    return parsed_answer

print("Acaparser initializes over.")

if __name__ == "__main__":
    img_path = "./model/sample.png"
    text = acaparser(img_path)
    print(text['<OCR>'])
```

## Citation

```
@misc{huawei2024aceparse,
      title={AceParse: A Comprehensive Dataset with Diverse Structured Texts for Academic Literature Parsing}, 
      author={Huawei Ji and Cheng Deng and Bo Xue and Zhouyang Jin and Jiaxin Ding and Xiaoying Gan and Luoyi Fu and Xinbing Wang and Chenghu Zhou},
      year={2024},
      eprint={2409.},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```

## Acknowledgments

This repository builds on top of the [Florence-2](https://huggingface.co/microsoft/Florence-2-base/tree/main) repository.
