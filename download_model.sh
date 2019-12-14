#!/usr/bin/env bash
cd "$(dirname "${0}")"
BASE_DIR="$(pwd)"

BASE_DIR="$(pwd)"
MODELS_DIRECTORY=generator/gpt2/models
MODEL_VERSION=model_v5

MODEL_DIRECTORY="${MODELS_DIRECTORY}"

MODEL_NAME=model-550
MODEL_TORRENT_URL="https://github.com/AIDungeon/AIDungeon/files/3935881/model_v5.torrent.zip"
MODEL_TORRENT_BASENAME="$(basename "${MODEL_TORRENT_URL}")"

download_torrent() {
  echo "Creating directories."
  mkdir -p "${MODEL_DIRECTORY}"
  cd "${MODEL_DIRECTORY}"
  wget "${MODEL_TORRENT_URL}"
  unzip "${MODEL_TORRENT_BASENAME}"
  which aria2c > /dev/null
  if [ $? == 0 ]; then
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
}

redownload () {
	echo "Deleting $MODEL_DIRECTORY"
	rm -rf ${MODEL_DIRECTORY}
	download_torrent
}

if [[ -d "${MODEL_DIRECTORY}" ]]; then
	ANSWER="n"
	echo "AIDungeon2 Model appears to be downloaded."
	echo "Would you like to redownload?"
	echo "WARNING: This will remove the current model![y/N]"
	read ANSWER
	ANSWER=$(echo $ANSWER | tr '[:upper:]' '[:lower:]')
	case $ANSWER in
		 [yY][eE][sS]|[yY])
			redownload;;
		*)
			echo "Exiting program!"
			exit;;
	esac
else
	download_torrent
fi
