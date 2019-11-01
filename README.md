# AIDungeon

This is the repo for AI Dungeon including the new version AI Dungeon 2 built with the 1.6B parameter CTRL model and fine tuned on post-apocalyptic fiction and crowd sourced text adventure samples. I'm currently working on a way to host it, but you can download and run the model yourself.

## Requirements
- GPU with 32GB of memory (though it could be quantized down. See https://github.com/salesforce/ctrl)
- Python3
- Relies on Tensorflow 1.14 which can be installed with `pip install tensorflow[-gpu]==1.14`
- [gsuti](https://cloud.google.com/storage/docs/gsutil_install)

## Installation
If you have the massive GPU to run it then you can install it by following the below instructions:
1. Clone the repo `git clone https://github.com/nickwalton/AIDungeon.git`
2. `cd AIDungeon`
3. `pip install -r requirements.txt`
4. `cd generator/ctrl`
5. `./install_ctrl_py3.sh`
6. `./download_model.sh`

## To Play
`python console_play.py`

If you want to change the game in interesting ways you can change the context and initial prompt in console_play.py. There's also more finetuned control code in generator/ctrl/ctrl_generator.py you can play around with. 
