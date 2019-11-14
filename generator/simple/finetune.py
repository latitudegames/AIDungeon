import gpt_2_simple as gpt2
import os
import requests

model_name = "1558M"
if not os.path.isdir(os.path.join("models", model_name)):
    print(f"Downloading {model_name} model...")
    gpt2.download_gpt2(model_name=model_name)  # model is saved into current directory under /models/124M/

file_name = "merged_first_person.txt"

sess = gpt2.start_tf_sess()
gpt2.finetune(sess,
              file_name,
              model_name=model_name,
              steps=10000)

gpt2.generate(sess)