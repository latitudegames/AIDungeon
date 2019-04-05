# AI-DungeonMaster

### AI Dungeon Master is an automatically generated text adventure that uses the GPT-2 model (smaller version) to generate completely AI made text adventures. 

## Installation
```
git clone http://github.com/nickwalton/AI-DungeonMaster
pip install regex
pip install numpy
pip install tensorflow
pip install tqdm
```

## (Optional) tensorflow-gpu
For faster performance you can instead install tensorflow-gpu, but you'll also need up to date nvidia graphics drivers and cuda. 
```
pip install tensorflow-gpu==1.12
```

## Download the GPT-2 Model
```
cd AI-DungeonMaster/gpt2
python download_model.py 117M
```

## Run the Game
```
cd ..
python dungeon_master.py
```
