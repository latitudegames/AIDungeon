#!/bin/bash
cd "$(dirname "${0}")"
BASE_DIR="$(pwd)"

MODELS_DIRECTORY=generator/gpt2/models
MODEL_VERSION=model_v5
MODEL_NAME=model-550
MODEL_TORRENT_URL="https://github.com/nickwalton/AIDungeon/files/3935881/model_v5.torrent.zip"
MODEL_TORRENT_BASENAME="$(basename "${MODEL_TORRENT_URL}")"

if [[ -d "${MODELS_DIRECTORY}/${MODEL_VERSION}" ]]; then
    echo "AIDungeon2 is already installed"
else
    echo "Downloading AIDungeon2 Model... (this may take a few minutes)"
    mkdir -p "${MODELS_DIRECTORY}"
    cd "${MODELS_DIRECTORY}"
    mkdir "${MODEL_VERSION}"
    apt-get install aria2 unzip > /dev/null
    wget "${MODEL_TORRENT_URL}"
    unzip "${MODEL_TORRENT_BASENAME}"
    aria2c -x 16 -s 32 --seed-time=0 "${MODEL_TORRENT_BASENAME%.*}"
    echo "Download Complete!"
    cd "${BASE_DIR}"
    pip install -r requirements.txt > /dev/null
fi
