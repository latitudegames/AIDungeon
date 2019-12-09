import os

from google.cloud import storage


class Cacher:
    def __init__(self, credentials_file, bucket_name="dungeon-cache"):
        # Model/Cache Info
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_file
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.get_bucket(bucket_name)
        pass

    def cache_file(self, seed, choices, response, tag, print_result=False):
        prompt_num = 0
        blob_file_name = "prompt" + str(prompt_num) + "/seed" + str(seed) + "/" + tag
        for action in choices:
            blob_file_name = blob_file_name + str(action)
        blob = self.bucket.blob(blob_file_name)

        blob.upload_from_string(response)

        if print_result:
            print("File ", blob_file_name, " cached")

    def retrieve_from_cache(self, seed, choices, tag, print_result=False):
        prompt_num = 0
        blob_file_name = "prompt" + str(prompt_num) + "/seed" + str(seed) + "/" + tag

        for action in choices:
            blob_file_name = blob_file_name + str(action)

        blob = self.bucket.blob(blob_file_name)

        if blob.exists(self.storage_client):
            result = blob.download_as_string().decode("utf-8")
            if print_result:
                print(blob_file_name, " found in cache")
        else:
            result = None
            if print_result:
                print(blob_file_name, " not found in cache")

        return result
