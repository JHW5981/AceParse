import os
import json
from metrics import get_metrics
from collections import Counter
import re

with open("./comparisons/all_math_characters.txt", "r") as fp:
    all_math_characters = [i.strip() for i in fp.readlines()]

all_metrics = {}
delete = True

# tesseract 
with open("./comparisons/results/tesseract.json") as fp:
    tesseract_results = json.load(fp)
tesseract_labels = tesseract_results['label']
tesseract_preds = tesseract_results['tesseract']
time_per_sample = tesseract_results['time_per_sample']
tesseract_metric = get_metrics(tesseract_labels, tesseract_preds, delete=delete)
length = len(tesseract_labels)
tesseract_metric['speed'] = time_per_sample*8307/length

for key, value in tesseract_metric.items():
    print(f"tesseract_{key}:{value}")

all_metrics["tesseract"] = tesseract_metric

# ppocr 
with open("./comparisons/results/ppocr.json") as fp:
    ppocr_results = json.load(fp)
ppocr_labels = ppocr_results['label']
ppocr_preds = ppocr_results['ppocr']
time_per_sample = ppocr_results['time_per_sample']
ppocr_metric = get_metrics(ppocr_labels, ppocr_preds, delete=delete)
length = len(ppocr_labels)
ppocr_metric['speed'] = time_per_sample*8307/length

for key, value in ppocr_metric.items():
    print(f"ppocr_{key}:{value}")

all_metrics["ppocr"] = ppocr_metric

# pix2text 
with open("./comparisons/results/pix2text.json") as fp:
    pix2text_results = json.load(fp)
pix2text_labels = pix2text_results['label']
pix2text_preds = pix2text_results['pix2text']
time_per_sample = pix2text_results['time_per_sample']
pix2text_metric = get_metrics(pix2text_labels, pix2text_preds, delete=delete)
length = len(pix2text_labels)
pix2text_metric['speed'] = time_per_sample*8307/length

for key, value in pix2text_metric.items():
    print(f"pix2text_{key}:{value}")

all_metrics["pix2text"] = pix2text_metric

# mineru 
with open("./comparisons/results/mineru.json") as fp:
    mineru_results = json.load(fp)
mineru_labels = mineru_results['label']
mineru_preds = mineru_results['mineru']
time_per_sample = mineru_results['time_per_sample']
mineru_metric = get_metrics(mineru_labels, mineru_preds)
length = len(mineru_labels)
mineru_metric['speed'] = time_per_sample*8307/length

for key, value in mineru_metric.items():
    print(f"mineru_{key}:{value}")

all_metrics["mineru"] = mineru_metric

# nougat 
with open("./comparisons/results/nougat.json") as fp:
    nougat_results = json.load(fp)
nougat_labels = nougat_results['label']
nougat_preds = nougat_results['nougat']
time_per_sample = nougat_results['time_per_sample']
nougat_metric = get_metrics(nougat_labels, nougat_preds, delete=delete)
length = len(nougat_labels)
nougat_metric['speed'] = time_per_sample*8307/length

for key, value in nougat_metric.items():
    print(f"nougat_{key}:{value}")

all_metrics["nougat"] = nougat_metric

with open("./metrics_delete.json", "w") as fp:
    json.dump(all_metrics, fp)

# acaparser 
def extract_ocr_content(text):
    # Define the regex pattern to find content between <ocr> and </ocr>
    pattern = re.compile(r'<ocr>(.*?)</ocr>', re.DOTALL)
    
    # Find all matches in the text
    matches = pattern.findall(text)
    
    return matches
with open("./comparisons/results/acaparser.json") as fp:
    acaparser_results = json.load(fp)

acaparser_labels = acaparser_results['label']
acaparser_labels = [i[151:-17] for i in acaparser_labels]

acaparser_preds = acaparser_results['acaparser']
acaparser_preds = [i["<OCR>"].strip("<ocr>") for i in acaparser_preds]

time_per_sample = acaparser_results['time_per_sample']
acaparser_metric = get_metrics(acaparser_labels, acaparser_preds)
length = len(acaparser_labels)
acaparser_metric['speed'] = time_per_sample*8307/length

for key, value in acaparser_metric.items():
    print(f"acaparser_{key}:{value}")

all_metrics["acaparser"] = acaparser_metric


with open(".comparisons/metrics.json", "w") as fp:
    json.dump(all_metrics, fp)