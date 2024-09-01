from transformers import AutoProcessor, AutoModelForCausalLM , DataCollatorForSeq2Seq, TrainingArguments, Trainer
from datasets import Dataset
import torch 
from PIL import Image
import os
import pandas as pd
import argparse

os.environ["WANDB_DISABLED"] = "true"

def get_args():
    parser = argparse.ArgumentParser(description="Parameters")

    parser.add_argument('--train_img_paths', default="./dataset/data/images/train_images.txt")
    parser.add_argument('--train_label_paths', default="./dataset/data/labels/train_labels.txt")
    parser.add_argument('--eval_img_paths', default="./dataset/data/images/val_images.txt")
    parser.add_argument('--eval_label_paths', default="./dataset/data/labels/val_labels.txt")
    parser.add_argument('--output_dir', default="./model/weights")
    
    
    args = parser.parse_args()
    return args

args = get_args()

# model
model_id = 'microsoft/Florence-2-base'
model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)
processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)  

def print_trainable_parameters(model):
    """
    Prints the number of trainable parameters in the model.
    """
    trainable_params = 0
    all_param = 0
    for _, param in model.named_parameters():
        all_param += param.numel()
        if param.requires_grad:
            trainable_params += param.numel()
    print(
        f"trainable params: {trainable_params} || all params: {all_param} || trainable%: {100 * trainable_params / all_param}"
    )

print_trainable_parameters(model)

# dataset
with open(args.train_img_paths, "r") as fp:
    train_img_paths = fp.read().splitlines()
with open(args.train_label_paths, "r") as fp:
    train_label_paths = fp.read().splitlines()
with open(args.eval_img_paths, "r") as fp:
    val_img_paths = fp.read().splitlines()
with open(args.eval_label_paths, "r") as fp:
    val_label_paths = fp.read().splitlines()
    
    
train_dataframe = {
    'img_path': train_img_paths,
    'label': train_label_paths
}
val_dataframe = {
    'img_path': val_img_paths,
    'label': val_label_paths
}

train_df = pd.DataFrame(train_dataframe)
train_ds = Dataset.from_pandas(train_df)
val_df = pd.DataFrame(val_dataframe)
val_ds = Dataset.from_pandas(val_df)

def tokenize_function(examples):
    img_path = examples['img_path']
    Image_obj = Image.open(img_path)
    pixel_values = processor.image_processor(Image_obj)['pixel_values'][0]
    pixel_values = torch.tensor(pixel_values)
    
    instruction = 'What is the text in the image?'
    input_ids = processor.tokenizer(
        instruction,
        return_tensors='pt',
        max_length=1024,
        truncation=True
    )['input_ids']

    label_path = examples['label']
    with open(label_path, "r", encoding='utf-8') as f:
        text = f.read().strip()
    text = text[199:-17]
    output = "<ocr>" + text + "</ocr>"
    labels = processor.tokenizer(
        output,
        return_tensors='pt',
        max_length=1024,
        truncation=True
    )['input_ids']

    return {
        'input_ids': input_ids.squeeze(),
        'pixel_values': pixel_values.squeeze(),
        'labels': labels.squeeze()
    }
    
train_ds = train_ds.map(tokenize_function, batched=False)
val_ds = val_ds.map(tokenize_function, batched=False)

train_ds.set_format(type='torch', columns=['input_ids', 'pixel_values', 'labels'])
val_ds.set_format(type='torch', columns=['input_ids', 'pixel_values', 'labels'])
# Data collator
data_collator = DataCollatorForSeq2Seq(
    processor.tokenizer,
    model=model.language_model,
    label_pad_token_id=-100,
    pad_to_multiple_of=None,
    padding=True
)

# Train
args = TrainingArguments(
    output_dir=args.output_dir,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=1,
    logging_steps=10,
    learning_rate=1e-5,
    num_train_epochs=100,
    eval_strategy="epoch",
    save_strategy="epoch",
    save_total_limit=1,
    load_best_model_at_end=True,
    metric_for_best_model='loss',
    greater_is_better=False,
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_ds,
    eval_dataset=val_ds,
    data_collator=data_collator,
)

trainer.train()