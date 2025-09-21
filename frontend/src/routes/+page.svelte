<script>

	import { browser } from "$app/environment"
	import { onMount } from "svelte";
	//console.log(browser);

	let robotIP = undefined;
	$: streamAddress = `http://${robotIP}:30303/stream.mjpg`;
	let inputWebSocket = undefined;


	onMount(() => {
		robotIP = window.location.hostname
		console.log(robotIP)

		inputWebSocket = new WebSocket(`ws://${robotIP}:30304`);
	})

	//const robotIP = window.location.hostname;


	function clamp(val, min, max) {
		return Math.min(Math.max(val, min), max);
	}

	// Throttle tates range from -1 to 1
	const controlState = {
		leftThrottle: 0,
		rightThrottle: 0,
		throttleMult: 1.0,
		cameraTiltAngle: 90,
		lightOn: false
	};

	const keysPressed = {
		"w": false,
		"a": false,
		"s": false,
		"d": false
	};

	function calculateAndSetState() {
		controlState.leftThrottle = clamp(
			keysPressed["a"] * -1 
			+ keysPressed["d"] * 1
			+ keysPressed["w"] * 1
			+ keysPressed["s"] * -1,
			-1, 1);

		controlState.rightThrottle = clamp(
			keysPressed["a"] * 1 
			+ keysPressed["d"] * -1
			+ keysPressed["w"] * 1
			+ keysPressed["s"] * -1,
			-1, 1);

	}

	function handleInput(event) {
		// Switching message format to something quicker than JSON would improve
		// performance. JSON is good enough for now

		console.log(event);

		if ("wasd".includes(event.key)) {
			keysPressed[event.key] = true ? event.type == "keydown" : false;

			calculateAndSetState()


		} else if (event.key == "r" && event.ctrlKey) {
			inputWebSocket = new WebSocket(`ws://${robotIP}:30304`);
		} else if (event.key == "q" && event.type == "keydown") {
			controlState.throttleMult = clamp(controlState.throttleMult - 0.1, 0, 1);
		} else if (event.key == "e" && event.type == "keydown") {
			controlState.throttleMult = clamp(controlState.throttleMult + 0.1, 0, 1);
		} else if (event.key == "x" && event.type == "keydown") {
			controlState.cameraTiltAngle = 
				clamp(controlState.cameraTiltAngle + 10, 0, 180);
		} else if (event.key == "z" && event.type == "keydown") {
			controlState.cameraTiltAngle = 
				clamp(controlState.cameraTiltAngle - 10, 0, 180);
		} else if (event.key == "f" && event.type == "keydown") {
			controlState.lightOn = !controlState.lightOn;
		}

		console.log(controlState);
		inputWebSocket.send(JSON.stringify(controlState));

	}

	function sendState() {
		inputWebSocket.send(JSON.stringify(controlState));
	}

	let joystickOn = false;


	function canvasMouseDown(event) {
		joystickOn = true;
	}

	const joystickX = 200;
	const joystickY = 200;

	function canvasMouseMove(event) {
		const centerx = joystickX / 2;
		const centery = joystickY / 2;

		const layerx = event.layerX;
		const layery = event.layerY;

		const dx = (layerx - centerx) / centerx;
		const dy = -1 * (layery - centery) / centery;

		const leftThrottle = clamp(dy + dx, -1, 1)
		const rightThrottle = clamp(dy - dx, -1, 1)


		controlState.leftThrottle = leftThrottle;
		controlState.rightThrottle = rightThrottle;
		if (joystickOn) {
			sendState()
		}
	}

	function canvasMouseUp(event) {
		joystickOn = false;

		controlState.leftThrottle = 0;
		controlState.rightThrottle = 0;
		sendState()
	}

</script>

<div style="position: relative;">
	<img src={streamAddress} tabindex="0"
						  on:keydown|preventDefault={handleInput}
						  on:keyup|preventDefault={handleInput}
						  style="width: 100vw"/>

	<div style="position: absolute; left: 0; top: 0;
	color: #eeeeee; background-color: #33333388; padding: 0.5rem">
		<input bind:value={robotIP}/>
		<p>Throttle (e/q): {controlState.throttleMult.toFixed(2) * 100}%</p>
		<p><button on:click={() => { controlState.lightOn = !controlState.lightOn; sendState() }}>Light (f)</button>: {controlState.lightOn ? "on" : "off"}</p>
		<p>
			Camera Tilt (x/z)
			<button on:click={() => { 
		   controlState.cameraTiltAngle = 
		   clamp(controlState.cameraTiltAngle + 10, 0, 180);
		   sendState();
		   }}>Up</button>
			<button on:click={() => {
		   controlState.cameraTiltAngle = 
		   clamp(controlState.cameraTiltAngle - 10, 0, 180);
		   sendState();
		   }}>Down</button>
		</p>
	</div>

	<div style="position: absolute; right: 0; top: 0; background-color: #33333388; border: 1px solid white; touch-action: none;">
		<canvas id="joystick" on:mousedown={canvasMouseDown} height={joystickY} width={joystickX}
																	on:mousemove={canvasMouseMove}
		  on:mouseup={canvasMouseUp}
		  on:touchstart={canvasMouseDown}
		  on:touchend={canvasMouseUp}
		  on:touchcancel={canvasMouseUp}
		  on:touchmove={canvasMouseMove}>
		</canvas>
	</div>
</div>

<style>
	div > * {
		margin: 0.25rem;
	}
</style>
