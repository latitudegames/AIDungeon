# Download the 512-length model if specified, 256-length otherwise
if [ "$1" = "512" ]
then
    URL="gs://sf-ctrl/seqlen512_v1.ckpt/"
else
    URL="gs://sf-ctrl/seqlen256_v1.ckpt/"
fi

gsutil -m cp -r "$URL" .
