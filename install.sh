MODELS_DIRECTORY=generator/gpt2/models
MODEL_VERSION=model_v5
MODEL_NAME=model-550
DOWNLOAD_URL=https://aidungeonmodel.s3-us-west-1.amazonaws.com

if [ -d "${MODELS_DIRECTORY}/${MODEL_VERSION}" ]; then
    echo "AIDungeon2 is already installed"

else
    cd ${MODELS_DIRECTORY}
    	echo "Downloading AIDungeon2 Model... (this may take a few minutes)"
    gsutil -m cp -r gs://ai_dungeon_awesomeness/model_v5 .
    echo "Download Complete!"
    cd ../../..

    pip install -r requirements.txt > /dev/null
fi
