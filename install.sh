MODEL_DIRECTORY=aidungeon/generator/gpt2/models/model_v1

if [ -d "$MODEL_DIRECTORY" ]; then
    echo "AIDungeon is already installed"

else
    echo "Installing AIDungeon"
    gsutil -m cp -r gs://aidungeon2model/model_v1 ./generator/gpt2/models
    pip install -r requirements.txt > /dev/null
fi
