using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Tensorflow;
using static Tensorflow.Binding;

namespace AIDungeon.net
{
    public class Sample
    {

        public static Tensor SampleSequence(IDictionary<string, int> hParams, int length, Tensor startToken,
            int batchSize, Tensor context, decimal temperature, int topK, int topP)
        {
            if (startToken == null)
            {
                if (context == null) throw new ArgumentNullException(nameof(context), $"Specify exactly one of {nameof(startToken)} and {nameof(context)}");
            }
            else
            {
                if (context != null) throw new ArgumentException($"Specify exactly one of {nameof(startToken)} and {nameof(context)}", nameof(context));
                context = tf.fill(new Tensor(new[]{batchSize, 1}), startToken);
            }

            using (var ns = tf.name_scope("sample_sequence"))
            {
                var initialState = Body((past: null, prev: context, output: context));
                var tokens = control_flow_ops.while_loop<(Tensor past, Tensor prev, Tensor output)>(Cond, Body,)
            }
        }

        private static (object logits, object presents) Step(IDictionary<string, int> hParams, Tensor tokens,
            Tensor past = null)
        {
            var lm_output = GPT2Model.Model(hParams, tokens, past, "model", _ReuseMode.AUTO_REUSE);
        }

        private static Tensor Cond((Tensor past, Tensor prev, Tensor output) _) => new Tensor(true);

        private static (Tensor past, Tensor prev, Tensor output) Body((Tensor past, Tensor prev, Tensor output) state)
        {

        }
    }
}
