# AIDungeon2

Read more about AIDungeon2 and how it was built [here](https://pcc.cs.byu.edu/2019/11/21/ai-dungeon-2-creating-infinitely-generated-text-adventures-with-deep-learning-language-models/).

Play the mobile app version of the game by following the links [here](https://aidungeon.io)

Play the game online by following this link [here](https://play.aidungeon.io)

Play the game in Colab [here](https://colab.research.google.com/github/AIDungeon/AIDungeon/blob/master/AIDungeon_2.ipynb).

To play the game locally, it is recommended that you have an nVidia GPU with 12 GB or more of memory, and CUDA installed. If you do not have such a GPU, each turn can take a couple of minutes or more for the game to compose its response. To install and play locally:
```
git clone --branch master https://github.com/AIDungeon/AIDungeon/
cd AIDungeon
./install.sh # Installs system packages and creates python3 virtual environment
./download_model.sh
source ./venv/bin/activate
./play.py
```

## Finetune the model yourself

Formatting the data. After scraping the data I formatted text adventures into a json dict structure that looked like the following:
```
{   
    "tree_id": <someid>
    "story_start": <start text of the story>
    "action_results": [
    {"action":<action1>, "result":<result1>, "action_results": <A Dict that looks like above action results>},
    {"action":<action2>, "result":<result2>, "action_results": <A Dict that looks like above action results>}]
}
```
Essentially it's a tree that captures all the action result nodes. 
Then I used [this](https://github.com/AIDungeon/AIDungeon/blob/develop/data/build_training_data.py) to transform that data into one giant txt file. The txt file looks something like:
```
<|startoftext|>
You are a survivor living in some place...
> You search for food
You search for food but are unable to find any
> Do another thing
You do another thing...
<|endoftext|>
(above repeated many times)
```

Then once you have that you can use the [finetuning script](https://github.com/AIDungeon/AIDungeon/blob/develop/generator/simple/finetune.py) to fine tune the model provided you have the hardware.

Fine tuning the largest GPT-2 model is difficult due to the immense hardware required. I no longer have access to the same hardware so there are two ways I would suggest doing it. I originally fine tuned the model on 8 32GB V100 GPUs (an Nvidia DGX1). This allowed me to use a batch size of 32 which I found to be helpful in improving quality. The only cloud resource I could find that matches those specs is an aws p3dn.24xlarge instance so you'd want to spin that up on EC2 and fine tune it there. (might have to also request higher limits). Another way you could do it is to use a sagemaker notebook (similar to a colab notebook) and select the p3.24xlarge instance type. This is equivalent to 8 16 GB V100 GPUs. Because each GPU has only 16GB memory you probably need to reduce the batch size to around 8.


Community
------------------------

AIDungeon is an open source project. Questions, discussion, and
contributions are welcome. Contributions can be anything from new
packages to bugfixes, documentation, or even new core features.

Resources:

* **Website**: [aidungeon.io](http://www.aidungeon.io/)
* **Email**: aidungeon.io@gmail.com
* **Twitter**: [creator @nickwalton00](https://twitter.com/nickwalton00), [dev @benjbay](https://twitter.com/benjbay)
* **Reddit**: [r/AIDungeon](https://www.reddit.com/r/AIDungeon/)
* **Discord**: [aidungeon discord](https://discord.gg/Dg8Vcz6)


Contributing
------------------------
Contributing to AIDungeon is easy! Just send us a
[pull request](https://help.github.com/articles/using-pull-requests/)
from your fork. Before you send it, summarize your change in the
[Unreleased] section of [the CHANGELOG](CHANGELOG.md) and make sure
``develop`` is the destination branch.

AIDungeon uses a rough approximation of the
[Git Flow](http://nvie.com/posts/a-successful-git-branching-model/)
branching model.  The ``develop`` branch contains the latest
contributions, and ``master`` is always tagged and points to the latest
stable release.

If you're a contributor, make sure you're testing and playing on `develop`.
That's where all the magic is happening (and where we hope bugs stop).
