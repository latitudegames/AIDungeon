
URL="https://storage.cloud.google.com/aidungoen2model/finetuned_model.tar.gz?folder&organizationId"

wget -O ./model "$URL"
cd model
tar -xvzf finetuned_model.tar.gz
cd ..