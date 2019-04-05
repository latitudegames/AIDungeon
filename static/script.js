var Typer={
	text: null,
	accessCountimer:null,
	index:0, 
	speed:2,
	init: function(){
		accessCountimer=setInterval(function(){Typer.blinkCursor();},500); 
	},
 
	content:function(){
		return $("#console").html();
	},
 
	addText:function(){
		var cont=Typer.content(); 
		if(cont.substring(cont.length-1,cont.length)=="|") 
			$("#console").html($("#console").html().substring(0,cont.length-1)); 

		Typer.index+=Typer.speed;	
		var text=Typer.text.substring(0,Typer.index)
		var rtn= new RegExp("\n", "g"); 

		$("#console").html(text.replace(rtn,"<br/>"));
		window.scrollBy(0,50); 
		
	},
 
	blinkCursor:function(){ 
		var cont=this.content(); 
		
		if(cont.substring(cont.length-1,cont.length)=="|") 
			$("#console").html($("#console").html().substring(0,cont.length-1)); 
		
		else
			$("#console").append("|");
	}
}


// request_story("Hello")
function requestStory(prompt){
	$.post("/generate", { story_block: true, prompt},
	  startTyping);
}


function startTyping(story){
    Typer.text=story
    addTextTimer = setInterval("typeWords();", 40);
 
}

function typeWords() {
	Typer.addText();
	
	if (Typer.index > Typer.text.length) {
		clearInterval(addTextTimer);
		
        var choice = prompt("What's your choice?");
        
        requestStory(prompt);
        // Here we probably want to call the request story function with the choice they made
        
	}
}

function start(){
    Typer.speed=2;

    Typer.init(); 
    startTyping("<span id='a'>Adventurer@DungeonDream</span>:<span id='b'>~</span><span id='c'>$</span> Hello Adventurer and welcome to my dungeon!");
}

addTextTimer = null;
start();
