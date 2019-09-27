# Fine-Tuning the Model on Custom Dataset


This folder contains sample code to fine-tune the model on custom data. It is primarily targeted for GPU usage, but there are pointers throughout showing how to run on TPUs as well. 

Fine-tuning can be used to augment existing control codes or add new control codes. There are 5 steps elaborated upon in the example below: 

1. Patch `keras.py` as in the generation script
2. Obtain raw versions of your text files
3. Convert this text data into TFRecords; _if you wish to use TPUs, you must transfer these records to GCS._
4. Fine-tuning the model on these TFRecords files
5. Testing that the generation works. 

## Example of adding a new control code

Let's begin by adding a new control code `Moby` that is associated with the book [Moby Dick](https://www.gutenberg.org/ebooks/2701)

If you run `generation.py` with the pretrained models available and try to use this control code, you will find that the model outputs gibberish. Great! It is indeed a fresh new control code. We will run this again after training as a sanity check. 

### Step 1 - Patch your `keras.py`
As is required for the generation script, you must patch your `keras.py`. If you patched it before, please roll-back and re-patch with the latest version. 

There are two changes: (1) it defaults to `use_tpu=False` so training/inference takes place on GPUs, (2) the batch size defaults to 4 for GPU training. You might need to go lower depending on your machine. 

You can leave `use_tpu=True` if you wish to train on TPUs and adjust the batch size accordingly. 

### Step 2 - Obtain Your Data

The book is available publicly; you can simply download it as 

```
wget -O moby_dick.txt https://www.gutenberg.org/files/2701/2701-0.txt
```

### Step 3 - Convert Data to TFRecords

We include the file `make_tf_records.py` to facilitate this.

Run:

```
python make_tf_records.py --text_file moby_dick.txt --control_code Moby --sequence_len 256
```

It has three arguments: `text_file` which specifies the name of the file to convert, `control_code` which specifies one token (must be in vocabulary) to append to each example, and `sequence_len` which specifies the sequence length to use to create the data. This must match the sequence length of the model being trained. 


### Step 4 - Train!

Simply run `python training.py --model_dir <path_to_model>.ckpt/ --iterations <number_of_iterations>`

The script picks up all TFRecords in the current folder and fine-tunes the model provided in the `--model_dir` flag. 

If you intend to use TPUs, you must transfer these TFRecords to GCS and edit the location of the data path used by `input_fn` to the GCS bucket. 

To very important gotchas here:

1. If you have very limited data, the model will very likely overfit and end up memorizing. At the moment, just keep the `--iterations` flag low, preferably equivalent to one epoch or so. 

2. The model is updated and stored in the same directory, if you don't wish to overwrite your model files, please create a backup before you run the training code. 

### Step 5 - Generate! 

We ran `python training.py --model_dir seqlen256_v1.ckpt/ --iterations 250` and try generating with the `Moby` control code. 

Running with the `Moby` control code and a prompt of `I` yields something reasonable in-domain:

```
Moby I <GENERATION_BEGINS> was a little fellow, and he was a
 great man, what should that matter? And yet it seemed to me that
 Queequegs words about his father were true. He had been very angry
 with him, because the old man would not let him go a-whaling...
```

Providing a prompt also works:

```
Moby Then I realized, it wasn't one white whale but three! <GENERATION_BEGINS> And all three
 were making straight for my boat, which was now some distance away.

 But the three spouts seemed to be coming from different directions, and
 as they drew nearer and nearer, their tongues began licking up the
 brine like so many hungry wolves at a carcass...
```

