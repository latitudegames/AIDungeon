initial_prompt = "You enter a dungeon with your trusty sword and shield. You are searching for the evil necromancer who killed your family. You've heard that he resides at the bottom of the dungeon, guarded by legions of the undead. You enter the first door and see"

start_text = "<span id='a'>Adventurer@AIDungeon</span>:<span id='b'>~</span><span id='c'>$</span> ./EnterDungeon \n <br/>"


var acceptInput=false
var inputStr = ""
var blinkCounter = 0
var action_list = ["You attack", "You tell", "You use", "You go"]

var StoryTracker = {
    firstStory: null,
    lastStory: null,
    lastAction: null,
    actions: [],
    results: [],
    action_int: 0,
    startPrompt: initial_prompt,
    
    getFirstStory:function(){
        console.log("Requesting first story")
        Typer.appendToText(initial_prompt)
        StoryTracker.requestStory(initial_prompt)
    
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
    
    addNextAction:function(action_result){
    
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
                
                if( /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent) ) {
                    setTimeout(StoryTracker.mobileButton, 1000);
                }
                
            }
        }
        
    },
    
    mobileButton:function(){
    
        if (Typer.index >= Typer.text.length -1){
            inputStr = window.prompt("What is your choice?","0");
            StoryTracker.processInput()
        }
        else{
            setTimeout(StoryTracker.mobileButton, 1000);
        }
    },
    
    makeActionRequests:function(prompt){
    
        StoryTracker.actions = []
        StoryTracker.results = []
        
        StoryTracker.requestAction(prompt)
        

    },
    
    requestStory:function(prompt){
	    $.post("/generate", {actions: false, prompt},
	      StoryTracker.addNextStory)
    },
    
    requestAction:function(prompt){
	    $.post("/generate", {actions: true, prompt},
	      StoryTracker.addNextAction)
    },

    processInput:function(){
        var choice_int = parseInt(inputStr, 10)
        
        if(choice_int >= 0 && choice_int <= 3){
            
            console.log("choice_int is %d", choice_int)
            StoryTracker.lastAction = StoryTracker.actions[choice_int]
            StoryTracker.lastStory = StoryTracker.results[choice_int]
            StoryTracker.makeActionRequests(StoryTracker.firstStory + StoryTracker.lastStory)
            Typer.appendToText("\n")
            Typer.appendToText(StoryTracker.lastStory)
            Typer.appendToText("\n\nOptions:")
        }
        else{
        
            Typer.appendToText("Invalid choice. Must be a number from 0 to 3. \n")
            Typer.appendToText("\nWhich action do you choose? ")
            acceptInput=true
            
            if( /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent) ) {
                setTimeout(StoryTracker.mobileButton, 1000);
            }
            
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
	    str = str.replace(".", "." + "<!-- laglaglaglaglaglaglaglaglaglag -->")
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
    addTextTimer = setInterval("typeWords()", 50)
 
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



