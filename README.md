# AIDungeon

This is the repo for AI Dungeon including the new version AI Dungeon 2 built with the 1.6B parameter CTRL model and fine tuned on post-apocalyptic fiction and crowd sourced text adventure samples. I'm currently working on a way to host it, but you can download and run the model yourself.

## Requirements
- GPU with 32GB of memory (though it could be quantized down. See https://github.com/salesforce/ctrl)
- Python3
- Relies on Tensorflow 1.14 which can be installed with `pip install tensorflow[-gpu]==1.14`
- [gsuti](https://cloud.google.com/storage/docs/gsutil_install)

## Installation
If you have the massive GPU to run it then you can install it by following the below instructions:
1. Clone the repo `git clone https://github.com/nickwalton/AIDungeon.git`
2. `cd AIDungeon`
3. `pip install -r requirements.txt`
4. `cd generator/ctrl`
5. `./install_ctrl_py3.sh`
6. `./download_model.sh`

## To Play
`python console_play.py`

If you want to change the game in interesting ways you can change the context and initial prompt in console_play.py. There's also more finetuned control code in generator/ctrl/ctrl_generator.py you can play around with. 

## Samples

> *Context: Long ago the bombs fell and the world ended. You are one of the few who is still alive. You are trying to survive by scavenging among the ruins of what is left behind. You walk for two hours and take a break. You've left the town you were in and are now in a more rural area. You look around you and see [Generation begins here] some hay that should provide you with enough protein to get through the night.*
>
> \> eat the hay then go to sleep
>
> You eat the hay then go to sleep. In the morning, you feel much better.
> \> Go to town
>
>> You walk for two hours and take a break. You've left the town you were in and are now in a more rural area. You look around you and see some hay that should provide you with enough protein to get through the night.
>
>\> eat the hay then go to sleep
> 
> You eat the hay then go to sleep. In the morning, you feel much better.
>
>\> Go to town
> 
> You go to town. The first store that comes into view has a sign in front reading, "Open 24 Hours". Great. Another town over goes under construction.
>
>\> go checkout the store
> 
>You go checkout the store. It's full of \*\*\*\*. Bottled Water, non - perishables, canned food, soft drinks, chips, pasta, cookies, candy, coffee, energy bars...
>
>\> fill your backup up with food
>
>You fill your backup up with food. You try not to think about it too much, but it's hard when your stomach starts rumbling.
>
\> eat some of the food
>
> You eat some of the food. It tastes horrible, like cardboard. Looking for something else to distract you, Ryan looks at his phone.
\> tell Ryan he's an idiot
>
> You tell Ryan he's an idiot. He hands you back your wallet. Seeing that you're well stocked up, he gives up.
\> leave the store and go look for other survivors
>
 You leave the store and go look for other survivors. There are plenty around, but they're all in different states of emergency.
\> ask someone if they need help
>
> You ask someone if they need help. They say no, everyone else seems ok, so you sit here alone on a roof with nothing to do. Suddenly, from nowhere, two more sirens blow.
\> go see what's going on
>
> You go see what's going on. There's another huge building fire up above you. You're probably safe right now.
\> run away from the burning building
>
>You run away from the burning building. It was completely empty. No sounds reach your ears but for the distant barking of some stray that looks hungry.
\> go give the stray some jerky
>
> You go give the stray some jerky. As soon as you're done eating, you hear a loud woof in the background.
>\> tell the dog you want to be friends and pet him
>
 >You tell the dog you want to be friends and pet him. The pooch gives his approval with an enthusiastic yip.
>\> leave with your dog to a nearby town
>
> You leave with your dog to a nearby town. On your way, you try not to dwell on how much you've let yourself go.
>\> keep walking to the town
>
> You keep walking to the town. It was dark when you're there, but then again, it isn't dark. There's streetlights now. People are moving around outside.
>\> go with your dog and talk to someone
>
> You go with your dog and talk to someone. She seems pretty surprised that someone has heard her story so far.
>\> ask her name
>
> You ask her name. She's Julie. Julie told you about a man breaking into an RV she stopped at on the way here.
>\> ask Julie if she knows where I can stay the night
>
> You ask Julie if she knows where you can stay the night. The woman looks shocked but then smiles in response as she hands over some bills. "Thanks," you say after looking them over.
>\> ask her where a hotel or inn is.
>
> You ask her where a hotel or inn is. "In this town, there's a Crown'' t Motel". She explains. 
\> go to Crown motel with your dog
>
> You go to Crown motel with your dog. The Crown's Crown'' Motel sits empty.
>\> find a room to sleep in in the motel
>
> You find a room to sleep in in the motel. It's nice and warm. With no other options, you try sleeping on the floor.
>\> tell my dog I've named him Scout 
>
> You tell your dog you've named him Scout. He seems unfazed so you put some blankets down for him.
>\> go to sleep next to Scout until morning
>
> You go to sleep next to Scout until morning. In the morning, you're feeling much better. Your wounds are beginning to heal nicely, though they look rather gross.
>\> clean my wounds and rebandage them. 
>
> You clean your wounds and rebandage them. . It doesn't take long before your bandaging skills begin to fail you. The pain in your arms intensifies.
>\> go see if Julie will help you bandage yourself
>
> You go see if Julie will help you bandage yourself. She refuses saying that she has enough on her plate.
>\> leave and see if someone else can help
>
> You leave and see if someone else can help. A man appears with a group healthcare kit. They tell you they have seen this before, but not as bad as today.
>\> ask him to bandage you up
>
> You ask him to bandage you up. As he does so, his whole body begins to shake violently. His pupils contract into slits, and his face >contorts in an effort to stay calm.
>\> ask what's wrong
>
> You ask what's wrong. He says nothing. You try talking again. 
>\> tell him he's freaking me out
>
> You tell him he's freaking you out. Still no response. Suddenly, your dog starts barking.
>\> back away slowly
>
> You back away slowly. Your dog's bark becomes a loud howl. It startles you.
>\> tell Scout your dog to run and get out of there
>
> You tell Scout your dog to run and get out of there. He does. And he begins his search for food.
>\> give scout some more jerky
>
> You give scout some more jerky. This jerky was made with real meat (not by-products) that were smoked over an open fire.
>\> eat some breakfast
> You eat some breakfast. Then, it gets dark. By dark, you're feeling extra hungry again. So, you go look for something else to snack on.
>\> go find somewhere to stay the night
>
> You go find somewhere to stay the night. It's dark out, but soon it'll begin to grow light. The light at least will help see your way around in the darkness.

