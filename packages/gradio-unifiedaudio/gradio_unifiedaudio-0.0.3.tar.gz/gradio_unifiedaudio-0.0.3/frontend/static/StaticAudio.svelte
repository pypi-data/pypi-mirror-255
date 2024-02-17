<script lang="ts">
	import { uploadToHuggingFace } from "@gradio/utils";
	import { Empty } from "@gradio/atoms";
	import { ShareButton, IconButton, BlockLabel } from "@gradio/atoms";
	import { Music } from "@gradio/icons";
	import type { I18nFormatter } from "@gradio/utils";
	import AudioPlayer from "../player/AudioPlayer.svelte";
	import { get_fetchable_url_or_file } from "@gradio/client";
	import { createEventDispatcher, onMount } from "svelte";
	import { FileData } from "@gradio/client";

	export let value: null | FileData = null;
	export let image: null | string | FileData = null;
	export let label: string;
	export let show_label = true;
	export let show_download_button = true;
	export let show_share_button = false;
	export let i18n: I18nFormatter;
	export let waveform_settings = {};
	export let root = "";
	export let proxy_url: string | null = null;
	let image_path: string;
	$: {
		if (image instanceof FileData) {
			image_path = image.path;
		} else {
			image_path = get_fetchable_url_or_file(image, root, proxy_url);
		}
	}

	const dispatch = createEventDispatcher<{
		change: FileData;
		play: undefined;
		pause: undefined;
		end: undefined;
		stop: undefined;
		clear: undefined;
	}>();
	$: value && dispatch("change", value);

	let audioElement;
	let isPlaying = false;

	function play_audio() {
		if (isPlaying) {
			audioElement.pause();
			isPlaying = false;
			return;
		} else {
			audioElement.play();
			isPlaying = true;
		}
	}

	function handle_audio_end(): void {
		dispatch("end");
	}
</script>

{#if value !== null}
	<div class="icon-buttons">
		{#if show_share_button}
			<ShareButton
				{i18n}
				on:error
				on:share
				formatter={async (value) => {
					if (!value) return "";
					let url = await uploadToHuggingFace(value.url, "url");
					return `<audio controls src="${url}"></audio>`;
				}}
				{value}
			/>
		{/if}
	</div>
	<audio src={value.url} controls bind:this={audioElement} on:ended={handle_audio_end}/>
	{#if image}
		<div class="image-container" on:click={play_audio} role="button" tabindex="0" aria-hidden="true">
			<img class="image-player" src={image_path} alt="test" />

			{#if !isPlaying}
				<!-- Play button -->
				<svg class="play-icon" viewBox="0 0 24 24" style="pointer-events: none;">
				<polygon points="5,3 19,12 5,21" fill="#fff" />
				</svg>
			{:else}
				<!-- Pause button -->
				<svg class="pause-icon" viewBox="0 0 24 24" style="pointer-events: none;">
				<rect x="6" y="4" width="4" height="16" fill="#fff" />
				<rect x="14" y="4" width="4" height="16" fill="#fff" />
				</svg>
			{/if}
			<div class="circle-container waveform-image" style="pointer-events: none;">
				{#each Array(15) as _, i (i)}
					<div class={`waveform-bar ${isPlaying ? `waveform-animation-${i % 5}` : ''}`} style={`height: ${20 + (i % 5) * 10}%`}></div>
				{/each}
			</div>
		</div>
	{:else}
		<div class="circle-container" on:click={play_audio} role="button" tabindex="0" aria-hidden="true">
			{#each Array(15) as _, i (i)}
				<div class={`waveform-bar ${isPlaying ? `waveform-animation-${i % 5}` : ''}`} style={`height: ${20 + (i % 5) * 10}%`}></div>
			{/each}
				{#if !isPlaying}
				<!-- Play button -->
				<svg class="play-icon" viewBox="0 0 24 24" style="pointer-events: none;">
				<polygon points="5,3 19,12 5,21" fill="#fff" />
				</svg>
			{:else}
				<!-- Pause button -->
				<svg class="pause-icon" viewBox="0 0 24 24" style="pointer-events: none;">
				<rect x="6" y="4" width="4" height="16" fill="#fff" />
				<rect x="14" y="4" width="4" height="16" fill="#fff" />
				</svg>
			{/if}
		</div>
	{/if}
{:else}
	<Empty size="small">
		<Music />
	</Empty>
{/if}

<style>

	audio {
		display: none;
	}

	.image-container {
		position: relative;
		width: 350px;
		height: 350px;
		margin: auto;
	}

	.image-player {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		border-radius: 50%;
		object-fit: cover;
	}

	.play-icon, .pause-icon {
		position: absolute;
		top: 50%;
		left: 50%;
		width: 75px;
		height: 75px;
		transform: translate(-50%, -50%);
	}

	.pause-icon {
		opacity: 0;
		transition: opacity 0.3s;
	}

	.image-container:hover .pause-icon, .circle-container:hover .pause-icon {
		opacity: 1;
	}

	.circle-container:hover .waveform-bar {
		opacity: 0.5;
	}

	.circle-container {
		position: relative;
		width: 350px;
		height: 350px;
		margin: auto;
		border-radius: 50%;
		border: 3px solid white;
		position: relative;
		overflow: hidden;
		display: flex;
		align-items: center;
		justify-content: center;
  	}

	.waveform-image {
		opacity: 0.5;
	}

	.waveform-bar {
	background-color: white;
	width: 2%;
	height: 20%;
	margin: 0 1%;
	border-radius: 5px;
	opacity: 0.5;
	transform-origin: bottom;
	}

	.waveform-animation-0 {
	animation: waveAnimation0 1s infinite ease-in-out;
	opacity: 1;
	}

	.waveform-animation-1 {
	animation: waveAnimation1 1.5s infinite ease-in-out;
	opacity: 1;
	}

	.waveform-animation-2 {
	animation: waveAnimation2 3s infinite ease-in-out;
	opacity: 1;
	}


	.waveform-animation-3 {
	animation: waveAnimation3 2s infinite ease-in-out;
	opacity: 1;
	}

	.waveform-animation-4 {
	animation: waveAnimation4 2.5s infinite ease-in-out;
	opacity: 1;
	}

	.waveform-animation-5 {
	animation: waveAnimation5 3.5s infinite ease-in-out;
	opacity: 1;
	}

	@keyframes waveAnimation0 {
	0%, 100% { height: 50%; }
	50% { height: 15%; }
	}

	@keyframes waveAnimation1 {
	0%, 100% { height: 45%; }
	50% { height: 25%; }
	}

	@keyframes waveAnimation2 {
	0%, 100% { height: 40%; }
	50% { height: 60%; }
	}

	@keyframes waveAnimation3 {
	0%, 100% { height: 70%; }
	50% { height: 25%; }
	}

	@keyframes waveAnimation4 {
	0%, 100% { height: 25%; }
	50% { height: 70%; }
	}

	@keyframes waveAnimation5 {
	0%, 100% { height: 60%; }
	50% { height: 15%; }
	}
</style>
