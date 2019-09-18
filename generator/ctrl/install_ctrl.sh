#!/bin/bash

# Gather CTRL and copy to working directory
git clone https://github.com/salesforce/ctrl.git model
cd model
# Cython is needed to compile fastBPE
pip install Cython

# Patch the TensorFlow estimator package
FILE="/usr/local/lib/python3.6/dist-packages/tensorflow_estimator/python/estimator/keras.py"
patch -b "$FILE" estimator.patch

# Install fastBPE
git clone https://github.com/glample/fastBPE.git
cd fastBPE
python setup.py install
cd ..

pip install tensorflow-gpu==1.14

curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Download the 512-length model if specified, 256-length otherwise
#if [ "$1" = "512" ]
#then
#    URL="gs://sf-ctrl/seqlen512_v1.ckpt/"
#else
#    URL="gs://sf-ctrl/seqlen256_v1.ckpt/"
#fi

# Copy model
#gsutil -m cp -r "$URL" .

