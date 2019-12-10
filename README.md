# AIDungeon2

### The model for AI Dungeon2 is temporarily unavailable to download due to cost. We're working on a solution!

Read more about AIDungeon2 and how it was built [here](https://pcc.cs.byu.edu/2019/11/21/ai-dungeon-2-creating-infinitely-generated-text-adventures-with-deep-learning-language-models/).

Play the game in Colab [here](http://www.aidungeon.io).

To play the game locally, it is recommended that you have an nVidia GPU with 12 GB or more of memory, and CUDA installed. If you do not have such a GPU, each turn can take a couple of minutes or more for the game to compose its response. To install and play locally:
```
git clone https://github.com/AIDungeon/AIDungeon/
cd AIDungeon
./install.sh
python3 play.py
```


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
Contributing to AIDungeon is relatively easy.  Just send us a
[pull request](https://help.github.com/articles/using-pull-requests/) from your fork.
When you send your request, make ``develop`` the destination branch on the
[AIDungeon repository](https://github.com/nickwalton/AIDungeon).

We prefer PRs to be
[PEP 8](https://www.python.org/dev/peps/pep-0008/) compliant.

AIDungeon uses a rough approximation of the
[Git Flow](http://nvie.com/posts/a-successful-git-branching-model/)
branching model.  The ``develop`` branch contains the latest
contributions, and ``master`` is always tagged and points to the latest
stable release.
