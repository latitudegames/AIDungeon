using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using Tensorflow;
using Tensorflow.Contrib.Train;
using static Tensorflow.Binding;

namespace AIDungeon.net
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();

            var config = new ConfigProto {GpuOptions = new GPUOptions {AllowGrowth = true}};
            var sess = tf.Session(config);
            var context = tf.placeholder(tf.int32, new TensorShape(1));

            var output = SampleSequence()
            
            var saver = tf.train.Saver();
            var ckpt = tf.train.latest_checkpoint(@"F:\src\AIDungeon\generator\gpt2\models\model_v5");
            saver.restore(sess, ckpt);
        }

        public object SampleSequence(HParams hparams, int length, string start_token, int batch_size, Tensor context,
            int temperature, int top_k, int top_p)
        {

        }
    }
}
