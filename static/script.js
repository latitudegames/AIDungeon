initial_prompt = "You enter a dungeon with your trusty sword and shield. You are searching for the evil necromancer who killed your family. You believe he is at the lowest level of the dungeon. You know you will encounter undead zombies and skeletons. You enter the first door and see"

start_text = "<span id='a'>Adventurer@AIDungeon</span>:<span id='b'>~</span><span id='c'>$</span> ./EnterDungeon \n <br/>"


var acceptInput=false
var inputStr = ""
var blinkCounter = 0

var StoryTracker = {
    firstStory: null,
    lastStory: null,
    lastAction: null,
    actions: null,
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
            
        StoryTracker.requestActions(StoryTracker.firstStory + StoryTracker.lastStory)
        Typer.appendToText(story)
    },
    
    addNextActions:function(actions){
        var actions = JSON.parse(actions)
        StoryTracker.actions = actions
        Typer.appendToText("\n\nOptions:")
        Typer.appendToText("\n0) " + actions[0])
        Typer.appendToText("\n1) " + actions[1])
        Typer.appendToText("\n2) " + actions[2])
        Typer.appendToText("\n3) " + actions[3])
        Typer.appendToText("\nWhich action do you choose? ")
        
        acceptInput = true
    },
    
    requestStory:function(prompt){
	    $.post("/generate", {actions: false, prompt},
	      StoryTracker.addNextStory)
    },
    
    requestActions:function(prompt){
	    $.post("/generate", {actions: true, prompt},
	      StoryTracker.addNextActions)
    },

    processInput:function(){
        var choice_int = parseInt(inputStr, 10)
        
        if(choice_int >= 0 && choice_int <= 3){
            
            console.log("choice_int is %d", choice_int)
            StoryTracker.lastAction = StoryTracker.actions[choice_int]
            StoryTracker.requestStory(StoryTracker.firstStory + StoryTracker.lastStory + StoryTracker.lastAction)
            
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
	    str = str.replace(".", "." + "<!-- laglaglaglaglaglaglag -->")
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
    addTextTimer = setInterval("typeWords()", 35)
 
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



