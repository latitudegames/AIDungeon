# CTRL - A Conditional Transformer Language Model for Controllable Generation
Authors: [Nitish Shirish Keskar](http://keskarnitish.github.io), [Bryan McCann](https://bmccann.github.io/), [Lav Varshney](http://www.varshney.csl.illinois.edu/), [Caiming Xiong](http://www.stat.ucla.edu/~caiming/), and [Richard Socher](https://www.socher.org/)

## Introduction


Large-scale language models show promising text generation capabilities, but
users cannot easily control this generation process. We release *CTRL*, a 1.6 billion-parameter conditional
transformer language model, trained to condition on control codes that specify
domain, subdomain, entities, relationships between entities, dates, and task-specific behavior. Control codes were derived from structure that naturally co-occurs with raw text, preserving the advantages of unsupervised learning while providing more explicit control over text generation.

Paper link: https://arxiv.org/abs/1909.05858

Blog link: https://blog.einstein.ai/introducing-a-conditional-transformer-language-model-for-controllable-generation/

The code currently supports two functionalities:
1. Generating from a trained model, two models are available for download - one with a sequence length of 256 and another with a sequence length of 512 -- they are trained with word-level vocabularies and through a sliding window approach can generate well beyond their trained sequence lengths. 
2. Source attribution - given a prompt, prints the perplexity of the prompt conditional on each domain control code (see Section 5 of the paper). 

Please refer to the argument flags for more details regarding the options available for either. 

## Table of Contents

1. [Citation](#citation)
2. [License](#license)
3. [Questions for Deliberation](#questions-for-deliberation)
4. [Usage](#usage)
5. [Sample Generations](#generations)
6. [Sample Source Attributions](#source-attributions)
7. [FAQs](#faqs)
8. [Get Involved](#get-involved)


## Citation
```
@article{keskarCTRL2019,
  title={{CTRL - A Conditional Transformer Language Model for Controllable Generation}},
  author={Keskar, Nitish Shirish and McCann, Bryan and Varshney, Lav and Xiong, Caiming and Socher, Richard},
  journal={arXiv preprint arXiv:1909.05858},
  year={2019}
}
```



## License
The code is released under the BSD-3 License (see `LICENSE.txt` for details), but we also ask that users respect the following:

This software should not be used to promote or profit from:

violence, hate, and division,

environmental destruction,

abuse of human rights, or 

the destruction of people's physical and mental health.

We encourage users of this software to tell us about the applications in which they are putting it to use by emailing ctrl-monitoring@salesforce.com, and to use [appropriate](https://arxiv.org/abs/1810.03993) [documentation](https://www.partnershiponai.org/about-ml/) when developing high-stakes applications of this model.

## Questions for Deliberation

We consulted extended members of the AI community in the responsible publication of this model. In particular, a preview of a [Partnership on AI (PAI)](http://partnershiponai.org) project relating to AI research publication norms was considered prior to the release of this work. While this PAI project is as-yet unpublished, it is informed by companies, organizations, and people differently affected by artificial intelligence and presents key considerations to evaluate before publishing potentially high-impact research.

The questions referenced from the early draft of the PAI project included:


1. How do you envision your research being used in the world? Who will use it? How much expertise is required to use it?
2. Who will use it?
3. Why would they be motivated to replicate / productionize your work?
4. How would a science fiction author turn your research into a dystopian story?
5. What is the worst way someone could use your research finding, given no resource constraints? 
6. What are the historical patterns of misuse or application in this area? How can the research be made more robust against  such misuse?
7. Which populations or communities will this technology negatively affect, deployed in the scenarios you envision? Will some groups be disproportionately affected?


## Usage

Here are the steps to get generating:

1. Install the dependencies

This code relies on [TensorFlow 1.14](https://www.tensorflow.org/install) and [fastBPE](https://github.com/glample/fastBPE). 

TensorFlow can be installed via `pip install tensorflow[-gpu]==1.14`. fastBPE installation instructions can be found in the GitHub repository linked above. We highly recommend experimenting within a virtualenv or Docker image. 

2. Patch the `/usr/local/lib/python2.7/dist-packages/tensorflow_estimator/python/estimator/keras.py` (or equivalent, if installed elsewhere) by running 

```patch -b <path_to_tensorflow_estimator_package>/python/estimator/keras.py estimator.patch```

We highly recommend experimenting within a virtualenv or Docker image since the workflow involves patching a TensorFlow file to support some custom functionality. This step is not optional; skipping this step will cause errors (irrespective of device).


3. Get the model files from `gs://sf-ctrl/seqlen256_v1.ckpt/` or `gs://sf-ctrl/seqlen512_v1.ckpt/`.

The model architecture is identical for both checkpoints. The former is trained with lower training sequence length (256) while the latter is trained with a larger one (512). We plan to update the models (with the appropriate version tags) as we continue to train them longer and on more data. **Our current recommendation is to use the `256_v1` model unless you have a strong reason not to. If you have no preference for domain, `Links` is always a good first choice.**

[With `gsutil` installed](https://cloud.google.com/storage/docs/gsutil_install), you can simply run `gsutil -m cp -r gs://sf-ctrl/seqlen256_v1.ckpt/ .` for copying the model checkpoint over. 

Without `gsutil`, you can follow the route recommended @ https://github.com/salesforce/ctrl/issues/7#issuecomment-531303214

4. Run the generation script `generation.py` or the source attribution script `source_attribution.py`. 

The `generation.py` prompts the user to input text and then prints the continuation. 
The `source_attribution.py` promps the user to input text and then prints a sorted list of domains and the perplexity of the text conditional on each individual domain. 


## Generations

The generations and attributions computed below have been generated using the `256` sequence length model. Comparable results can be obtained from the `512` version of the model as well. We demonstrate only a few of the functionalities, especially the control codes. For a complete list of the control codes, and how to use them, please refer to the paper. Note that `<GENERATION_BEGINS>` is only included for demonstrative purposes and is not actually generated by the model. 

1. Links

```
Links In a shocking finding, scientist discovered a herd of unicorns living in a remote, previously unexplored valley, in the Andes Mountains. Even more surprising to the researchers was the fact that the unicorns spoke perfect English.

<GENERATION_BEGINS> 

The scientists were able to track down the unicorn population by analyzing their DNA. They found out that they are descended from an ancient species called the “Tapiri,” which is believed to have been extinct for over 10,000 years.

 According to scientists, this discovery proves that there may be other undiscovered creatures on our planet.

 “We believe these animals could still exist and we hope to find them one day,” said Dr. Carlos Jaramillo, director of the National Geographic Society’s Center for Biodiversity Research at the University of Arizona.

 Scientists also confirmed that the Unicorn Genome Project has already identified several genes associated with the animal’s unique horn structure.

 “The genome project will help us understand how the animal evolved its horns so it can better protect itself against predators like jaguars or pumas.” 
 
 Researchers say that if all goes well, the new genetic information should allow them to create a 3D model of the animal.

 “It would give us a much clearer picture about what makes the creature unique.”- Dr David Sillito, lead researcher ...
 ```

As a generate note, you don't have to use greedy sampling. You can switch to `topk` or `nucleus` through the appropriate argument flags. 

Running it with `--temperature 0.2` and `--topk 5` yields:

```
Links In a shocking finding, scientist discovered a herd of unicorns living in a remote, previously unexplored valley, in the Andes Mountains. Even more surprising to the researchers was the fact that the unicorns spoke perfect English.

 The scientists were able to track down and capture one of these unicorn herds as it roamed through the valley for several days. They then took DNA samples from each animal and compared them with other animals found throughout the region.

 Advertisement

 What they found is truly astounding.

 According to the scientists, there are approximately 50 different species of unicorn, all of which live on two continents — North America and South America...
```


2. Wikipedia 


```
Wikipedia Salesforce Inc. is <GENERATION_BEGINS> a software company that provides cloud computing and business management software. It was founded in 1999 by Marc Benioff as an online retailer of enterprise software, but it has since expanded into other areas such as e-commerce, customer relationship management, and digital media...
```


3. Reviews

```
Reviews Rating: 1.0 <GENERATION_BEGINS> 
 I bought this for my son who is a huge fan of the show. He was so excited to get it and when he opened it, we were all very disappointed. The quality of the product is terrible. It looks like something you would buy at a dollar store.
Rating: 1.0
 This item arrived in poor condition. There are several scratches on the front cover as well as some other minor damage...
```

```
Reviews Rating: 4.0 <GENERATION_BEGINS> 
 I bought this for my husband and he loves it. He has a small wrist so it is hard to find watches that fit him well. This one fits perfectly.
 Rating: 4.0
 The watch looks great but the band was too big even though i had read other reviews about how large the bands were.
 Rating: 4.0
 It works well as an everyday watch. It's not very fancy or anything, just simple with no extra bells & whistles.
 
```

4. Books

```
Books Weary with toil, I haste me to my bed, <GENERATION_BEGINS> 
 And sleep the slumber of a weary man.
 The morning sun is up, and shines on high;
 My bed is ready, but no friend appears.
 A little while ago he came in sight,
 But now he's gone, as if he'd never come.
 He left his hat upon the table there,
 His coat was hanging up behind the door;
 And, when at last I looked around, there stood
 No one beside me, nor within call.
 Oh, what shall I do? What can be done?
 I'm sure that some strange accident has happened.
 I'll go out into the street again,
 To seek for him, or call him back again.
 But, oh, how lonely it will seem
 When all are gone who once were near me!
 ```

5. Reddit - r/running
```
Running Title: <GENERATION_BEGINS> I just ran my first 5k in under 30 minutes.
 Text: It was a pretty easy run, but it felt great.

 My goal is to run at least 10 miles per week for the next few months.

 I'm not sure if this qualifies as running or not, but it's definitely something that I've been wanting to do since high school.

 Thanks r/running!

 Edit: Thank you all so much for your kind words and advice.

 Edit 2: Wow, thanks guys!
```

6. Reddit - r/fitness
```
Fitness Title: <GENERATION_BEGINS> How do you get your body to burn fat when you're not working out?
 Text: I know that the reason why people lose weight is because they are eating less and burning more calories than their bodies need but how does this work for someone who doesn't have a lot of time or energy to exercise?

 For example, if I'm at home doing nothing all day then I'll be able to eat whatever I want without feeling like I've eaten too much. But what happens after that?

 EDIT: Thanks everyone for the responses!
 ```


7. Reddit - r/frugal

```
Saving Title: <GENERATION_BEGINS> How to get a free credit report
 Text: I have been trying for months now and it seems like no one is willing to give me one.

 Is there any way that you can just go online and fill out the forms yourself or do they require some sort of ID or something?

 Edit: Thanks everyone for your help!

 Edit 2: Thank you all so much for helping me!
```

8. Reddit - r/personalfinance

```
Finance Title: <GENERATION_BEGINS> I have a question about my credit score.
 Text: So I'm currently in the process of applying for an auto loan and I've been told that if you don't pay your bills on time then they will not approve you.

 My questions are:

 1. How do I know when to start paying off debt?
 2. What is the best way to get out of debt without having to file bankruptcy?
 3. Is it possible to refinance my car loan?
 4. Should I just wait until after school starts so I can take advantage of lower interest rates?
 5. If so, how long should I wait?

 Thanks
```

9. Questions

```
Questions Q: What is the capital of Australia? <GENERATION_BEGINS>
 A: Canberra
 Q: How many people live in Canberra?
 A: 650,000
 ```

10. Translation

```
Translation English : This is a natural language processing model that aims to generate coherent text in a controllable manner. ; French : <GENERATION_BEGINS> 
Il s'agit d'un modèle de traitement du langage naturel qui vise à générer un texte cohérent et contrôlable.
```

```
Translation English : This is a natural language processing model that aims to generate coherent text in a controllable manner. ; German : <GENERATION_BEGINS> 
Es handelt sich um ein natürliches Textverarbeitungssystem, das auf eine einheitliche und kontrollierbare Erzeugung von Text abzielt.
```




## Source Attributions

1. `I lost 10 lbs! Feeling great!`

```
PROMPT: I lost 10 lbs! Feeling great!
Diet ppl = 28.960714
Weight ppl = 29.223865
Fitness ppl = 36.162671
...
```

2. `My landlord is suing me for unpaid rent`

```
PROMPT: My landlord is suing me for unpaid rent
Legal ppl = 21.210965
Finance ppl = 24.619064
Saving ppl = 27.923208
...
```

3. `And then I saw him, the man in the mirror.`

```
PROMPT: And then I saw him, the man in the mirror.
Horror ppl = 17.919299
Scary ppl = 18.587843
Writing ppl = 23.154564
...
```

4. `Anarchism is an anti-authoritarian political philosophy that rejects hierarchies deemed unjust and advocates their replacement with self-managed, self-governed societies based on voluntary, cooperative institutions.`

```
PROMPT: Anarchism is an anti-authoritarian political philosophy that rejects hierarchies deemed unjust and advocates their replacement with self-managed, self-governed societies based on voluntary, cooperative institutions.
Wikipedia ppl = 34.446701
News ppl = 34.484165
Links ppl = 35.460126
...
```
5. `I love God`

```
PROMPT: I love God
Christianity ppl = 55.653985
Atheism ppl = 116.811038
Confessions ppl = 133.619834
...
```

## FAQs
(We hope to update this section frequently). 

1. Will you be releasing the training code and data?

We plan to release the training code soon. We will not be releasing the training data, but we will release tips and scripts related to data collection.

2. Is a version of the model available in PyTorch? 

Not at the moment, but if we come across an equivalent implementation, we will update this section. 

3. The code errors out.

Make sure that you have performed the patch as described above. If the error persists, please create a GitHub issue. 

4. The code generates non-sense irrespective of the prompt. 

Make sure that you have (a) provided the right `--model_dir` and that the folder actually exists and has the checkpoint, (b) provided a valid source code as the first token, and (c) tried generating with a simple prompt such as `Links I` or `Books From`. If the error persists, please create a GitHub issue. 
 



## Get Involved

Please create a GitHub issue if you have any questions, suggestions, requests or bug-reports. 
We welcome PRs!
