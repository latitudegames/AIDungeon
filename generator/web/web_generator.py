from generator.tf.src.encoder import *
import googleapiclient.discovery
import traceback

project = "ai-adventure"
model = "generator_v1"
version = "version2"

class WebGenerator():

    def __init__(self, credentials_file):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file
        model_path = './generator/tf/models/117M'
        self.enc = get_encoder(model_path)

    def predict(self, context_tokens):
        service = googleapiclient.discovery.build('ml', 'v1')
        name = 'projects/{}/models/{}'.format(project, model)
        instance = context_tokens

        if version is not None:
            name += '/versions/{}'.format(version)

        response = service.projects().predict(
            name=name,
            body={'instances': [{'context': instance}]}
        ).execute()

        if 'error' in response:
            raise RuntimeError(response['error'])

        return response['predictions']

    def generate(self, prompt, options={}):
        while (True):
            context_tokens = self.enc.encode(prompt)
            try:
                pred = self.predict(context_tokens)
                pred = pred[0]["output"][len(context_tokens):]
                output = self.enc.decode(pred)
                return output
            except:
                traceback.print_exc()
                print("generate request failed, trying again")
                continue
