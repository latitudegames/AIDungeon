using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Tensorflow;
using static Tensorflow.Binding;

namespace AIDungeon.net
{
    public class GPT2Model
    {
        public static Dictionary<string, int> DefaultHParams()
        {
            return new Dictionary<string, int>
                {{"n_vocab", 0}, {"n_ctx", 1024}, {"n_embd", 768}, {"n_head", 12}, {"n_layer", 12}};
        }

        public static object Model(IDictionary<string, int> hParams, Tensor x, Tensor past, string scope, _ReuseMode autoReuse)
        {
            using (var varScope = tf.variable_scope(name: scope, reuse: autoReuse == _ReuseMode.AUTO_REUSE))
            {
                var results = new Dictionary<string, object>();
                (int batch, Tensor sequence) = ShapeList(x);
                
                var wpe = tf.get_variable("wpe", new TensorShape(hParams["n_ctx"], hParams["n_embd"]),
                    initializer: tf.random_normal_initializer(stddev: 0.01F));

                var wte = tf.get_variable("wte", new TensorShape(hParams["n_vocab"], hParams["n_embd"]),
                    initializer: tf.random_normal_initializer(stddev: 0.02F));

                var past_length = past == null ? new Tensor(0) : tf.shape(past)[past.shape.Length - 1];

                var h = tf.gather(wte, x) + tf.gather(wpe, PositionsFor(x, past_length));
            }
        }

        private static Tensor PositionsFor(Tensor tokens, Tensor pastLength)
        {
            var batch_size = tf.shape(tokens)[0];
            var nSteps = tf.shape(tokens)[1];
            return ExpandTile(pastLength + tf.range(nSteps), batch_size);
        }

        private static Tensor ExpandTile(Tensor value, Tensor size)
        {
            var outValue = tf.convert_to_tensor(value, name: "value");
            var nDims = outValue.shape.Length;
            var multiples = new Tensor()
            return tf.tile<Tensor>(tf.expand_dims(value, axis: 0), size + new Tensor(1) * nDims);
        }

        private static (int batch, Tensor sequence) ShapeList(Tensor x)
        {
            return (x.shape[0], tf.shape(x)[1]);
        }
    }
}
