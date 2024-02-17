<script lang="ts">
	import { onMount } from "svelte";
	import RecordPlugin from "wavesurfer.js/dist/plugins/record.js";

	export let record: RecordPlugin;
	export let dispatch: (event: string, detail?: any) => void;

	let recordButton: HTMLButtonElement;
	let stopButton: HTMLButtonElement;

	onMount(() => {
		recordButton = document.getElementById("record") as HTMLButtonElement;
		stopButton = document.getElementById("stop") as HTMLButtonElement;
	});

	function record_click() {
		if (isRecording) {
			record.stopRecording();
			dispatch("stop_recording");
		} else {
			record.startRecording();
			dispatch("start_recording");
		}
		isRecording = !isRecording;
	}

	let isRecording = false;
</script>

	<div class="wrapper">
		{#if !isRecording}
			<button
				bind:this={recordButton}
				class="record-button"
				on:click={record_click}
			>
				<div class="microphone-icon">
					<img
					width="200"
					height="200"
					src="https://img.icons8.com/material-rounded/200/microphone.png"
					alt="microphone"
					/>
				</div>
			</button>
		{:else}
			<button
				bind:this={stopButton}
				class="stop-button"
				on:click={record_click}
			>
				<div class="stop-icon pulsate">
					<img
					width="200"
					height="200"
					src="https://img.icons8.com/material-rounded/200/stop.png"
					alt="stop"
					/>
				</div>
			</button>
		{/if}
	</div>

<style>
	.wrapper {
		display: flex;
		align-items: center;
		justify-content: center;
		align-items: center;
		border-radius: 50px;
	}

	.microphone-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
	}

	.stop-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
	}

	.record-button {
		height: 350px;
		width: 350px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		background: white;
		border: 6px solid rgb(0, 140, 255);
	}

	.stop-button {
		height: 350px;
		width: 350px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		background: white;
		border: 6px solid red;
	}


  @keyframes pulsate {
    0% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.1);
    }
    100% {
      transform: scale(1);
    }
  }

  .pulsate {
    animation: pulsate 1s infinite;
  }

	.record-button:disabled {
		cursor: not-allowed;
		opacity: 0.5;
	}

	@keyframes scaling {
		0% {
			background-color: var(--primary-600);
			scale: 1;
		}
		50% {
			background-color: var(--primary-600);
			scale: 1.2;
		}
		100% {
			background-color: var(--primary-600);
			scale: 1;
		}
	}
</style>
