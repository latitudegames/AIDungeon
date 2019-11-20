MODEL_DIRECTORY=aidungeon/generator/gpt2/models/model_v4

if [ -d "$MODEL_DIRECTORY" ]; then
    echo "AIDungeon2 is already installed"

else
    echo "Downloading AIDungeon2 Model"
    gsutil -m cp -r gs://aidungeon2model/model_v4 ./generator/gpt2/models
    pip install -r requirements.txt > /dev/null
fi
