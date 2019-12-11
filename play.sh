#!/bin/bash

source .env

aria2c -V -d"${MODELS_DIRECTORY}" "${MODELS_DIRECTORY}/${MODEL_TORRENT_BASENAME%.*}" > /dev/null &

python play.py
