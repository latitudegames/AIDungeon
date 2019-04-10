var prompts = ["You enter a dungeon with your trusty sword and shield. You are searching for the evil necromancer who killed your family and have heard that he resides at the bottom of the dungeon, guarded by legions of the undead. You enter the first door and see"]

start_text = "<span id='a'>Adventurer@AIDungeon</span>:<span id='b'>~</span><span id='c'>$</span> ./EnterDungeon \n <br/><!-- laglaglaglaglaglaglaglaglaglaglag-->"


var acceptInput=false
var action_waiting = false
var inputStr = ""
var typing = false
var blinkCounter = 0
var action_list = ["You attack", "You tell", "You use", "You go"]
var prompt_num = 0
var seed_max = 100
var seed_min = 0
var seed = Math.floor(Math.random() * (+seed_max - +seed_min)) + +seed_min; 
//var seed = 108
console.log("Seed is ", seed)

var StoryTracker = {
    firstStory: null,
    lastStory: null,
    lastAction: null,
    actions: [],
    results: [],
    choices: [],
    action_int: 0,
    startPrompt: prompts[prompt_num],
    
    getFirstStory:function(){
        console.log("Requesting first story")
        Typer.appendToText(StoryTracker.startPrompt)
        StoryTracker.requestFirstStory(StoryTracker.startPrompt)
    
    },
    
    addNextStory:function(story){
        StoryTracker.lastStory = story
        if (StoryTracker.firstStory == null){
            StoryTracker.firstStory = StoryTracker.startPrompt + story
        }
            
        StoryTracker.makeActionRequests(StoryTracker.firstStory + StoryTracker.lastStory)
        Typer.appendToText(story)
        Typer.appendToText("\n\nOptions:")
    },
    
    actionWait:function(){
        console.log("action waiting ", action_waiting)
        console.log("typing ", typing)
        if(action_waiting == true || typing){
            setTimeout(StoryTracker.actionWait, 2000);
        }
        else{
            Typer.appendToText(" Generating...")
        }
    
    },
    
    addNextAction:function(action_result){
    
        action_waiting = false
    
        var action_results = JSON.parse(action_result)
    
        for (i = 0; i < 4; i++){
            
            action_result = action_results[i]

            action = action_result[0]
            result = action_result[1]
            
            StoryTracker.actions.push(action)
            StoryTracker.results.push(result)
            var print_action = "\n" + String(StoryTracker.action_int) + ") " + action
            StoryTracker.action_int += 1
            Typer.appendToText(print_action)

            if (StoryTracker.action_int > 3){
                Typer.appendToText("\nWhich action do you choose? ")
                StoryTracker.action_int = 0
                acceptInput = true
                
            }
        }
        
    },
    
    makeActionRequests:function(prompt){
    
        StoryTracker.actions = []
        StoryTracker.results = []
        
        StoryTracker.requestActions(prompt, JSON.stringify(StoryTracker.choices))
    },

    
    requestFirstStory:function(prompt){
	    $.post("/generate", {actions: false, seed, prompt_num},
	      StoryTracker.addNextStory)
    },
    
    requestActions:function(prompt, choices){
	    $.post("/generate", {actions: true, seed, prompt_num, prompt, choices},
	      StoryTracker.addNextAction)
    },

    processInput:function(){
        var choice_int = parseInt(inputStr, 10)
        
        if(choice_int >= 0 && choice_int <= 3){
            
            console.log("choice_int is %d", choice_int)
            StoryTracker.choices.push(choice_int)
            StoryTracker.lastAction = StoryTracker.actions[choice_int]
            StoryTracker.lastStory = StoryTracker.results[choice_int]
            StoryTracker.makeActionRequests(StoryTracker.firstStory + StoryTracker.lastStory)
            action_waiting = true
            setTimeout(StoryTracker.actionWait, 2000);
            Typer.appendToText("\n")
            Typer.appendToText(StoryTracker.lastStory)
            Typer.appendToText("\n\nOptions:")
        }
        else{
        
            Typer.appendToText("Invalid choice. Must be a number from 0 to 3. \n")
            Typer.appendToText("\nWhich action do you choose? ")
            acceptInput=true
            
        }
        
        
        inputStr = ""
    }
}

var Typer={
	text: null,
	accessCountimer:null,
	index:0, 
	speed:2,
	startBlinker: function(){
		accessCountimer=setInterval(function(){Typer.blinkCursor()},500) 
	},
 
	content:function(){
		return $("#console").html()
	},
	
	appendToText:function(str){
	    str = str.replace(".", "." + "<!-- laglag-->")
	    typing = true
	    Typer.text = Typer.text + str;
	},
 
	addText:function(){
	
	    if (Typer.index <= Typer.text.length) {
		    var cont=Typer.content() 
		    if(cont.substring(cont.length-1,cont.length)=="|") 
			    $("#console").html($("#console").html().substring(0,cont.length-1)) 

            if (Typer.text.substring(Typer.index, Typer.index + Typer.speed).includes(".")){
                Typer.index += 1
            }
		    else{
		    Typer.index+=Typer.speed
		    }	
		    var text=Typer.text.substring(0,Typer.index)
		    var rtn= new RegExp("\n", "g") 

		    $("#console").html(text.replace(rtn,"<br/>"))
		    window.scrollBy(0,50) 
		}
		else{
		    typing = false
		}
		
	},
 
	blinkCursor:function(){ 
	
	    if(blinkCounter > 10){
		    var cont=this.content() 
		
		    if(cont.substring(cont.length-1,cont.length)=="|") 
			    $("#console").html($("#console").html().substring(0,cont.length-1)) 
		
		    else
			    $("#console").append("|")
		}
		else{
		    blinkCounter += 1
		}
	}
}


function writeAppend(str){
    $("#console").append(str)

}


function startTyping(){
    addTextTimer = setInterval("typeWords()", 25)
 
}

function typeWords() {
	Typer.addText()
}

document.onkeypress = function(evt) {

    if(acceptInput){
        evt = evt || window.event
        var charCode = evt.keyCode || evt.which

        if(charCode == 13){
            acceptInput = false
            Typer.appendToText("\n\n")
            StoryTracker.processInput(inputStr)
        }
        else{
        
            var charStr = String.fromCharCode(charCode)
            Typer.appendToText(charStr)
            inputStr = inputStr + charStr
        }
        
    }
}

function start(){
    
    Typer.speed=1
    Typer.text = ""
    Typer.appendToText(start_text)
    
    StoryTracker.getFirstStory()

    startTyping()
    Typer.startBlinker()
}


$(document).ready(function() {
    start()
})



