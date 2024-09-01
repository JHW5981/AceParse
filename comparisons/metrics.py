from multiprocessing import Pool
from collections import defaultdict
from typing import List
import nltk
from nltk import edit_distance
import re

with open("/home/jihuawei2/维是勉哉/SDPD/comparison/all_math_characters.txt", "r") as fp:
    all_math_characters = [i.strip() for i in fp.readlines()]

def preprocess_delete(text, all_math_characters=all_math_characters):
    math_characters_pattern = '|'.join(re.escape(char) for char in all_math_characters)
    # 用正则表达式进行分割并保留分割符号
    split_pattern = f'({math_characters_pattern})'
    split_content = re.split(split_pattern, text)
    result = [part for part in split_content if part]
    result_split = []
    for item in result:
        item = item.strip()
        if len(item) == 0:
            continue
        elif item in all_math_characters:
            continue
        else:
            result_split.extend(item.split())
    return result_split

def preprocess(text, all_math_characters=all_math_characters):
    math_characters_pattern = '|'.join(re.escape(char) for char in all_math_characters)
    # 用正则表达式进行分割并保留分割符号
    split_pattern = f'({math_characters_pattern})'
    split_content = re.split(split_pattern, text)
    result = [part for part in split_content if part]
    result_split = []
    for item in result:
        item = item.strip()
        if len(item) == 0:
            continue
        elif item in all_math_characters:
            result_split.append(item)
        else:
            result_split.extend(item.split())
    return result_split
    
def compute_metrics(pred, gt, minlen=4, delete: bool = False):
    metrics = {}
    if len(pred) < minlen or len(gt) < minlen:
        return metrics
    metrics["edit_dist"] = edit_distance(pred, gt) / max(len(pred), len(gt))
    if delete:
        reference = preprocess_delete(gt)
        hypothesis = preprocess_delete(pred) 
    else:  
        reference = preprocess(gt)
        hypothesis = preprocess(pred)
    # reference = gt.split()
    # hypothesis = pred.split()
    metrics["bleu"] = nltk.translate.bleu([reference], hypothesis)
    reference = set(reference)
    hypothesis = set(hypothesis)
    metrics["precision"] = nltk.scores.precision(reference, hypothesis)
    metrics["recall"] = nltk.scores.recall(reference, hypothesis)
    metrics["f_measure"] = nltk.scores.f_measure(reference, hypothesis)
    return metrics


def get_metrics(gt: List[str], pred: List[str], pool: bool = True, delete: bool = False):
    metrics = defaultdict(list)
    if pool:
        with Pool() as p:
            _metrics = p.starmap(compute_metrics, iterable=zip(pred, gt))
    else:
        _metrics = [compute_metrics(p, g, delete=delete) for p, g in zip(pred, gt)]
    for m in _metrics:
        for key, value in m.items():
            metrics[key].append(value)
    metrics = dict(metrics)
    ave_metrics = {key: sum(values) / len(values) for key, values in metrics.items()}
    return ave_metrics


if __name__ == "__main__":
    pred =  "\\begin{table}[h]\n    \\centering\n    \\begin{tabular}{lcccc}\n    \\toprule\n    Model & \\textbf{LMEH} & \\textbf{VEL} & \\textbf{OAIE} & \\textbf{HE} \\\\\n    \\midrule\n    gpt-3.5-turbo (ChatGPT) & & 1110 & 0.87 & 0.72 \\\\\n    EleutherAI/pythia-12b & 60.33 \\\\\n    OpenAssistant/pythia-12b-sft-v8-7k-steps & 60.28 & 997 & 0.10 & 0.10 \\\\\n    tiiuae/falcon-40b & 72.29 \\\\\n    OpenAssistant/falcon-40b-sft-top1-560 & 74.04 & 1192 & 0.26 & 0.09 \\\\\n    OpenAssistant/falcon-40b-sft-mix-1226 & 74.40 & 1053 & 0.44 & 0.13 \\\\\n    huggyllama/llama-65b & 67.24 \\\\\n    OpenAssistant/oasst-sft-7e3-llama-30b & 68.03 & 979 & 0.52 & 0.20 \\\\\n    OpenAssistant/oasst-rlhf-3-llama-30b-5k-steps & 68.51 & 1068 & 0.51 & 0.15 \\\\\n    \\bottomrule\n    \\end{tabular}\n    \\caption{Comparison of model evaluation scores on different LLM benchmarks:\n    \\textbf{LMEH:} lm-evaluation-harness (eval-harness) (average scores, see online leaderboard for more details)\n    \\textbf{VEL:} Vicuna Elo Rank [78]\n    \\textbf{OAIE:} OpenAI Evals (openai2023gpt4)\n    \\textbf{HE:} HumanEval [91]\n    (for all benchmarks, higher is better).\n    We have chosen to leave the Hugging Face Hub identifiers as the model names for identifiability.\n    }\n\\end{table}"

    gt = "\\begin{table}[h]\n    \\centering\n    \\begin{tabular}{lcccc}\n    \\toprle\n    Model & \\textbf{LMEH} & \\textf{VEL} & \\textbf{OAIE} & \\textbf{HE} \\\\\n    \\midrule\n    gpt-3.5-turbo (ChatGPT) & & 1110 & 0.87 & 0.72 \\\\\n    EleutherAI/pythia-12b & 60.33 \\\\\n    OpenAssistant/pythia-12b-sft-v8-7k-steps & 60.28 & 997 & 0.10 & 0.10 \\\\\n    tiiuae/falcon-40b & 72.29 \\\\\n    OpenAssistant/falcon-40b-sft-top1-560 & 74.04 & 1192 & 0.26 & 0.09 \\\\\n    OpenAssistant/falcon-40b-sft-mix-1226 & 74.40 & 1053 & 0.44 & 0.13 \\\\\n    huggyllama/llama-65b & 67.24 \\\\\n    OpenAssistant/oasst-sft-7e3-llama-30b & 68.03 & 979 & 0.52 & 0.20 \\\\\n    OpenAssistant/oasst-rlhf-3-llama-30b-5k-steps & 68.51 & 1068 & 0.51 & 0.15 \\\\\n    \\bottomrule\n    \\end{tabular}\n    \\caption{Comparison of model evaluation scores on different LLM benchmarks:\n    \\textbf{LMEH:} lm-evaluation-harness (eval-harness) (average scores, see online leaderboard for more details)\n    \\textbf{VEL:} Vicuna Elo Rank [78]\n    \\textbf{OAIE:} OpenAI Evals (openai2023gpt4)\n    \\textbf{HE:} HumanEval [91]\n    (for all benchmarks, higher is better).\n    We have chosen to leave the Hugging Face Hub identifiers as the model names for identifiability.\n    }\n\\end{table}"

    print(preprocess_delete(pred))
