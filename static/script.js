start_text = "<span id='a'>Adventurer@AIDungeon</span>:<span id='b'>~</span><span id='c'>$</span> ./EnterDungeon <br/><!-- laglaglaglaglaglaglaglaglaglaglag-->"

function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) 
};

// Used to control the terminal like screen typing 
var Typer={
	text:null,
	inputStr:"",
	index:0, 
	speed:2,
	acceptInput:false,
	inputReady:false,
	
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

	sendInput:function(){
        request = Typer.inputStr
	    $.post("/generate", {action: request}, receiveResponse)
	    Typer.inputStr = ""
	},

	startTyping:function(){
        addTextTimer = setInterval("Typer.addText()", 20)
    },


    KeyCheck:function(evt) {
        evt = evt || window.event
        var charCode = evt.keyCode || evt.which
        if(charCode == 8){
            if(inputStr.length > 0){
                console.log(inputStr)
                inputStr = inputStr.substring(0, inputStr.length-1)
                console.log(inputStr)
                Typer.removeChar()
            }
        }
    },

    onKeyPressFunc:function(evt) {

        if(Typer.acceptInput && !isMobileDevice()){
            evt = evt || window.event
            var charCode = evt.keyCode || evt.which

            if(charCode == 13){
                Typer.acceptInput = false
                Typer.sendInput()
            }
            else{
                var charStr = String.fromCharCode(charCode)
                Typer.appendToText(charStr)
                Typer.inputStr = Typer.inputStr + charStr
            }

        }
    },
}

function onButtonClick(num){

    document.getElementById('buttons').style.visibility='hidden';

    if (Typer.acceptInput == true){
        Typer.acceptInput = false
        num = String(num)
        Typer.appendToText(num)
        Typer.inputStr = num
        Typer.sendInput
    }
}

function receiveResponse(text){

    Typer.appendToText(text)
    Typer.acceptInput = true
}

function start(){

    Typer.speed=1
    Typer.text = ""
    Typer.appendToText(start_text)
    Typer.startTyping()
    request_str = ""
	$.post("/generate", {action: request_str}, receiveResponse)
    document.getElementById('buttons').style.visibility='hidden';
}

document.onkeypress = Typer.onKeyPressFunc
document.addEventListener("keydown", Typer.KeyCheck);
$(document).ready(function() {
    start()
})

