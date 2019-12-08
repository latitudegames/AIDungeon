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
    echo "Downloading AIDungeon2 Model... (this may take a very, very long time)"
    mkdir -p "${MODELS_DIRECTORY}"
    cd "${MODELS_DIRECTORY}"
    mkdir "${MODEL_VERSION}"
    apt-get install aria2 unzip > /dev/null
    wget "${MODEL_TORRENT_URL}"
    unzip "${MODEL_TORRENT_BASENAME}"
    echo -e "\n\n==========================================="
    echo "We are now starting to download the torrent."
    echo "It will take a while to get up to speed."
    echo "After download completes, we will seed this for 1 minute to ensure high availability."
    echo "DHT errors are normal."
    echo -e "===========================================\n"
    aria2c \
        --max-connection-per-server 16 \
        --split 32 \
        --bt-max-peers 300 \
        --bt-enable-lpd \
        --seed-time=1 \
        --summary-interval=15 \
        --disable-ipv6 \
        "${MODEL_TORRENT_BASENAME%.*}"
    echo "Download Complete!"
    cd "${BASE_DIR}"
    pip install -r requirements.txt > /dev/null
fi
