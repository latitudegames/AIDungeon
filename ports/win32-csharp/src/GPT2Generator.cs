using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Tensorflow;
using static Tensorflow.Binding;

namespace AIDungeon.net
{
    public class GPT2Generator
    {
        public static readonly Random rng = new Random();

        public int GenerateNum { get; set; }
        public decimal Temp { get; set; }
        public decimal TopK { get; set; }
        public decimal TopP { get;set; }
        public bool Censor { get; set; }
        public string ModelName { get; set; }
        public string ModelDir { get; set; }
        public string CheckpointPath { get; set; }
        public int BatchSize { get; set; }
        public int Samples { get; set; }
        public Encoder Encoder { get; set; }
        public Session Session { get; set; }
        public Tensor Context { get; set; }
        public object Output { get; set; }


        public GPT2Generator(int generateNum, decimal temperature, decimal topK, decimal topP, bool censor)
        {
            GenerateNum = generateNum;
            Temp = temperature;
            TopK = topK;
            TopP = topP;
            Censor = censor;

            ModelName = "model_v5";
            ModelDir = "generator/gpt2/models";
            CheckpointPath = Path.Combine(ModelDir, ModelName);

            var modelsDir = Environment.ExpandEnvironmentVariables(ModelDir);
            BatchSize = 1;
            Samples = 1;

            Encoder = Encoder.GetEncoder(ModelName, modelsDir);
            var hParams =
                JsonConvert.DeserializeObject<Dictionary<string, int>>(
                    File.ReadAllText(Path.Combine(modelsDir, ModelName, "hparams.json")));
            foreach (var kvp in GPT2Model.DefaultHParams())
            {
                if (!hParams.ContainsKey(kvp.Key)) hParams[kvp.Key] = kvp.Value;
            }

            var seed = rng.Next(100001);

            var config = new ConfigProto {GpuOptions = new GPUOptions {AllowGrowth = true}};
            Session = tf.Session(config);
            Context = tf.placeholder(tf.int32, new TensorShape(BatchSize));
            Output = Sample.SampleSequence();
        }
    }
}
