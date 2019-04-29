start_text = "<span id='a'>Adventurer@AIDungeon</span>:<span id='b'>~</span><span id='c'>$</span> ./EnterDungeon \n <br/><!-- laglaglaglaglaglaglaglaglaglaglag-->"

var acceptInput=false
var action_waiting = false
var inputStr = ""
var typing = false
var action_list = ["You attack", "You tell", "You use", "You go"]
var prompt_num = 0
var seed_max = 100
var seed_min = 0;
prompts = ["You enter a dungeon with your trusty sword and shield. You are searching for the evil necromancer who killed your family. You've heard that he resides at the bottom of the dungeon, guarded by legions of the undead. You enter the first door and see"]

if(seed == -1){
    var seed = Math.floor(Math.random() * (+seed_max - +seed_min)) + +seed_min;
}

 
//var seed = 999
console.log("Seed is ", seed)

function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) 
};


function buttonCheck(){
    if(typing == true){
        setTimeout(buttonCheck, 500);
    }
    else{
        document.getElementById('buttons').style.visibility='visible';
    }
}

var StoryTracker = {
    lastActionResult: "",
    actions: [],
    results: [],
    choices: [],
    
    // Requests the first story
    getFirstStory:function(){
        console.log("Requesting first story")
        Typer.appendToText(prompts[prompt_num])
        StoryTracker.requestFirstStory()
    
    },
    
    addFirstStory:function(story){
        StoryTracker.lastActionResult = story
        StoryTracker.makeActionRequests()
        Typer.appendToText(story)
    },
    
    // Called after requesting options, prints generating msg if waits too lng
    actionWait:function(){
    
        if(action_waiting == true){
            if(typing == true || acceptInput == true){
                setTimeout(StoryTracker.actionWait, 10000);
            }
            else{
                Typer.appendToText("\n\n Generating options... (~20s)")
            }
        }
    
    },
    
    // Callback for action request
    addNextAction:function(action_result){
    
        // Response receieved no longer waiting
        var action_results = JSON.parse(action_result)
        Typer.appendToText("\n\nOptions:")
        
        action_waiting = false
        StoryTracker.actions = []
        StoryTracker.results = []

        for (i = 0; i < 4; i++){
            
            action_result = action_results[i]

            action = action_result[0]
            result = action_result[1]
            
            StoryTracker.results.push(result)
            var print_action = "\n" + String(i) + ") " + action
            Typer.appendToText(print_action)

            if (i == 3){
                Typer.appendToText("\nWhich action do you choose? ")
                
                // Now we wait for the user to give input to us.    
                acceptInput = true
                
                if(isMobileDevice()){
                    setTimeout(buttonCheck, 500);
                }
            }
        }   
    },
    
    // Make a request to the server for result actions
    makeActionRequests:function(){
        action_waiting = true
        setTimeout(StoryTracker.actionWait, 10000);   
        StoryTracker.requestActions(StoryTracker.lastActionResult, JSON.stringify(StoryTracker.choices))
    },
    
    requestFirstStory:function(){
	    $.post("/generate", {actions: false, seed, prompt_num},
	      StoryTracker.addFirstStory)
    },
    
    requestActions:function(last_action_result, choices){
	    $.post("/generate", {actions: true, seed, prompt_num, last_action_result, choices},
	      StoryTracker.addNextAction)
    },

    // Called once a choice has been made by button or entering. 
    processInput:function(){
        var choice_int = parseInt(inputStr, 10)
        if(choice_int >= 0 && choice_int <= 3){
            
            console.log("choice_int is %d", choice_int)
            StoryTracker.choices.push(choice_int)
            StoryTracker.lastActionResult = StoryTracker.results[choice_int]
            StoryTracker.makeActionRequests(StoryTracker.firstStory + StoryTracker.lastStory)
            action_waiting = true
            Typer.appendToText("\n")
            Typer.appendToText(StoryTracker.lastActionResult)
        }
        else{
        
            Typer.appendToText("Invalid choice. Must be a number from 0 to 3. \n")
            Typer.appendToText("\nWhich action do you choose? ")
            acceptInput = true
            
                        
            if(isMobileDevice()){
                setTimeout(buttonCheck, 500);
            }
        
            
        }
        
        
        inputStr = ""
    }
}

// Used to control the terminal like screen typing 
var Typer={
	text: null,
	index:0, 
	speed:2,
	
	content:function(){
		return $("#console").html()
	},
	
	appendToText:function(str){
	    str = str.replace(".", "." + "<!-- laglaglag-->")
	    typing = true
	    Typer.text = Typer.text + str;
	},
	
	removeChar:function(){
	   var cont=Typer.content() 
	   $("#console").html($("#console").html().substring(0,cont.length-1))
	   Typer.text = Typer.text.substring(0, Typer.text.length-1)
	   Typer.index = Typer.index - 1
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
		}
		else{
		    typing = false
		}
		
	},
}


function writeAppend(str){
    $("#console").append(str)

}


function startTyping(){
    addTextTimer = setInterval("typeWords()", 20)
}


function typeWords() {
	Typer.addText()
}

document.addEventListener("keydown", KeyCheck);

function KeyCheck(evt) {
    evt = evt || window.event
    var charCode = evt.keyCode || evt.which
    if(charCode == 8){
        console.log("delete pressed")
        if(inputStr.length > 0){
            console.log(inputStr)
            inputStr = inputStr.substring(0, inputStr.length-1)
            console.log(inputStr)
            Typer.removeChar()
        }
    }
}


document.onkeypress = function(evt) {

    if(acceptInput && !isMobileDevice()){
        evt = evt || window.event
        var charCode = evt.keyCode || evt.which
        
        console.log(typeof charCode)     
        console.log("Char code is " + charCode)

        if(charCode == 13){
            acceptInput = false
            Typer.appendToText("\n")
            StoryTracker.processInput(inputStr)
        }
        else{
            var charStr = String.fromCharCode(charCode)
            Typer.appendToText(charStr)
            inputStr = inputStr + charStr
        }
        
    }
}

function onButtonClick(num){

    document.getElementById('buttons').style.visibility='hidden'; 

    if (acceptInput == true){
        acceptInput = false
        num = String(num)
        Typer.appendToText(num)
        Typer.appendToText("\n")
        inputStr = num
        StoryTracker.processInput()
    }
}

function start(){
    
    Typer.speed=1
    Typer.text = ""
    Typer.appendToText(start_text)
    
    StoryTracker.getFirstStory()

    startTyping()

    console.log("Not mobile device");
    document.getElementById('buttons').style.visibility='hidden'; 
}


$(document).ready(function() {
    start()
})

