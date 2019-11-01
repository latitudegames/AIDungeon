curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init


URL="gs://aidungeon2model/finetuned_model.tar.gz"

gsutil -m cp -r "$URL" model
cd model
tar -xvzf finetuned_model.tar.gz
cd ..