using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;
using Newtonsoft.Json.Utilities;
using System.IO;
using System.Text.RegularExpressions;

namespace AIDungeon.net
{
    public class Encoder
    {
        public IDictionary<string, int> EncodeDict { get; protected set; }
        public IDictionary<int, string> DecodeDict { get; protected set; }
        public string Errors { get; set; }
        public IDictionary<int, char> ByteEncoder { get; set; }
        public IDictionary<char, int> ByteDecoder { get; set; }
        public IDictionary<Tuple<string, string>, int> BpeRanks { get; set; }
        public IDictionary<string, string> Cache { get; set; }
        public Regex Pattern { get; set; }
        public Encoder(Dictionary<string, int> encoder, IEnumerable<Tuple<string, string>> bpeMerges, string errors = "replace")
        {
            EncodeDict = encoder;
            DecodeDict = encoder.ToDictionary(kvp => kvp.Value, kvp => kvp.Key);
            Errors = errors;
            ByteEncoder = BytesToUnicode();
            ByteDecoder = ByteEncoder.ToDictionary(kvp => kvp.Value, kvp => kvp.Key);
            BpeRanks = bpeMerges.Select(BpeConverter).ToDictionary(kvp => kvp.Key, kvp => kvp.Value);
            Cache = new Dictionary<string, string>();
            Pattern = new Regex(@"'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+");
        }

        private IDictionary<int, char> BytesToUnicode()
        {
            const int start1 = '!';
            const int end1 = '~';
            const int start2 = '¡';
            const int end2 = '¬';
            const int start3 = '®';
            const int end3 = 'ÿ';

            var dict = new Dictionary<int, char>();
            for (var i = start1; i <= end1; i++)
            {
                dict[i] = Convert.ToChar(i);
            }
            for (var i = start2; i <= end2; i++)
            {
                dict[i] = Convert.ToChar(i);
            }
            for (var i = start3; i <= end3; i++)
            {
                dict[i] = Convert.ToChar(i);
            }

            var n = 0;
            for (var b = 0; b <= 0xFF; b++)
            {
                if (dict.ContainsKey(b)) continue;
                dict[b] = Convert.ToChar(0x100 + n++);
            }

            return dict;
        }

        private static KeyValuePair<Tuple<string, string>, int> BpeConverter(Tuple<string, string> tuple, int idx) =>
            new KeyValuePair<Tuple<string, string>, int>(tuple, idx);

        public static Encoder GetEncoder(string modelName, string modelsDir)
        {
            var encoder =
                JsonConvert.DeserializeObject<Dictionary<string, int>>(
                    File.ReadAllText(Path.Combine(modelsDir, modelName, "encoder.json")));

            var bpeMerges = new List<Tuple<string, string>>(File
                .ReadAllLines(Path.Combine(modelsDir, modelName, "vocab.bpe")).Skip(1).Select(SplitWhitespace)
                .Where(NotNull));

            return new Encoder(encoder, bpeMerges);
        }

        private static Tuple<string, string> SplitWhitespace(string input)
        {
            var output = input.Split(' ');
            if (output.Length != 2) return null;
            return new Tuple<string, string>(output[0], output[1]);
        }

        private static bool NotNull(Tuple<string, string> input) => input != null;
    }
}
