curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init


URL="gs://sf-ctrl/seqlen512_v1.ckpt/"

gsutil -m cp -r "$URL" model
