


def present ():
	return """
<!DOCTYPE html>		
<body
	style="
		padding: 20px;
		background: #222;
		color: #DDD;
	"
>
<h1>Treasury</h1>

<p>Keys 2,3,4,5,W,E,R,T,S,D,F,G,X,C,V,B adapt into hexadecimal values.</p>
<div 
	tabindex="0" 
	
	id="seed"
	style="
		font-size: 2em;
	
		font-family: monospace, sans-serif;
	
		font-weight: bold;
		letter-spacing: 3px;
		
	
		word-wrap: break-word;
	
		box-sizing: border-box;
		min-height: 150px;
		width: 100%;
		border: 4px solid white;
		
		padding: 20px;
		
		border-radius: 6px;
	"
></div>

<div 
	tabindex="0" 
	id="seed-hex-count"
	style="
		margin-top: 4px;
	
		box-sizing: border-box;
		word-wrap: break-word;
		width: 100%;
		min-height: 50px;
		padding: 10px;
		border: 4px solid white;
		
		border-radius: 6px;
	"
></div>

<button id="build-public-key-button"


	style="
		font-size: 2em;
		padding: 10px;
		
		box-sizing: border-box;
	
		margin-top: 4px;
	
		background: none;
		border: 4px solid white;
		color: white;
		
		border-radius: 6px;
		
		cursor: pointer;
	"
>build public key</button>

<style>
seed::focus {
	border: 4px solid #39F;	
}

::selection {
	background: white;
	color: black;
}

</style>

<script>

legend = {
	"2": "0",
	"3": "1",
	"4": "2",
	"5": "3",
	"w": "4",
	"e": "5",
	"r": "6",
	"t": "7",
	"s": "8",
	"d": "9",
	"f": "A",
	"g": "B",
	"x": "C",
	"c": "D",
	"v": "E",
	"b": "F"
}

var seed_crate = document.getElementById ("seed")
var seed_hex_count_crate = document.getElementById ("seed-hex-count")
var build_public_key_button = document.getElementById ("build-public-key-button")

var seed_hex = ""
var seed_hex_count = 0
document.getElementById ("seed").addEventListener ("keyup", (event) => {
	if (event.isComposing || event.keyCode === 229) {
		return;
	}
	
	var ctrlKey = event.ctrlKey;
	var shiftKey = event.shiftKey;
	var metaKey = event.metaKey;
	
	key = event.key;
	
	if (seed_hex_count < 114 && typeof (legend [key]) === "string") {
		seed_hex += legend [key]
		seed_crate.textContent = seed_hex
		seed_hex_count += 1
		
		seed_hex_count_crate.textContent = seed_hex_count.toString () + " of 114" 
		
		console.log ({ seed_hex })
	}
		


	console.log (event)

	
});


build_public_key_button.addEventListener ("click", async (event) => {
	const response = await fetch ("/", {
		method: "patch",
		body: JSON.stringify ({
			"label": "form proposal keys",
			"fields": {
				"seed": seed_hex
			}
		})
	});
	const response_JSON = await response.json ();
	console.log (response_JSON);
})

function onkeyup (event) {
	console.log (event)
	
}

</script>
</body>
		"""