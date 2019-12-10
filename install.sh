#!/bin/bash
cd "$(dirname "${0}")"
BASE_DIR="$(pwd)"

MODELS_DIRECTORY=generator/gpt2/models
MODEL_VERSION=model_v5
MODEL_NAME=model-550
MODEL_TORRENT_URL="https://github.com/AIDungeon/AIDungeon/files/3935881/model_v5.torrent.zip"
MODEL_TORRENT_BASENAME="$(basename "${MODEL_TORRENT_URL}")"

if [[ -d "${MODELS_DIRECTORY}/${MODEL_VERSION}" ]]; then
    echo "AIDungeon2 is already installed"
else
    echo "Installing dependencies"
    pip install -r requirements.txt > /dev/null
    apt-get install aria2 unzip > /dev/null
    
    echo "Downloading AIDungeon2 Model... (this may take a very, very long time)"
    mkdir -p "${MODELS_DIRECTORY}"
    cd "${MODELS_DIRECTORY}"
    mkdir "${MODEL_VERSION}"
    wget "${MODEL_TORRENT_URL}"
    unzip "${MODEL_TORRENT_BASENAME}"
    echo -e "\n\n==========================================="
    echo "We are now starting to download the model."
    echo "It will take a while to get up to speed."
    echo "DHT errors are normal."
    echo -e "===========================================\n"
    aria2c \
        --max-connection-per-server 16 \
        --split 64 \
        --bt-max-peers 500 \
        --seed-time=0 \
        --summary-interval=15 \
        --disable-ipv6 \
        "${MODEL_TORRENT_BASENAME%.*}"
    echo "Download Complete!"
fi
