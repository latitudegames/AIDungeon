cd model
curl -sSL https://sdk.cloud.google.com | bash
gsutil -m cp gs://aidungeon2model/finetuned_model.tar.gz


tar -xvzf finetuned_model.tar.gz
cd ..