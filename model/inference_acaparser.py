from transformers import AutoProcessor, AutoModelForCausalLM
from tqdm import tqdm
import json
from PIL import Image
import time
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
