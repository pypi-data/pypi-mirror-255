<script lang="ts">
	import { onMount, onDestroy, createEventDispatcher } from "svelte";
	import { Upload, ModifyUpload } from "@gradio/upload";
	import { upload, prepare_files, type FileData } from "@gradio/client";
	import AudioPlayer from "../player/AudioPlayer.svelte";
	import { _ } from "svelte-i18n";

	import type { IBlobEvent, IMediaRecorder } from "extendable-media-recorder";
	import type { I18nFormatter } from "js/app/src/gradio_helper";
	import AudioRecorder from "../recorder/AudioRecorder.svelte";
	import StreamAudio from "../streaming/StreamAudio.svelte";
	import { SelectSource } from "@gradio/atoms";

	export let value: null | FileData = null;
	export let label: string;
	export let root: string;
	export let show_label = true;
	export let sources:
		| ["microphone"]
		| ["upload"]
		| ["microphone", "upload"]
		| ["upload", "microphone"] = ["microphone", "upload"];
	export let pending = false;
	export let streaming = false;
	export let i18n: I18nFormatter;
	export let waveform_settings = {};
	export let dragging: boolean;
	export let active_source: "microphone" | "upload";
	export let handle_reset_value: () => void = () => {};

	$: dispatch("drag", dragging);

	// TODO: make use of this
	// export let type: "normal" | "numpy" = "normal";
	let recording = false;
	let recorder: IMediaRecorder;
	let mode = "";
	let header: Uint8Array | undefined = undefined;
	let pending_stream: Uint8Array[] = [];
	let submit_pending_stream_on_pending_end = false;
	let inited = false;

	const STREAM_TIMESLICE = 500;
	const NUM_HEADER_BYTES = 44;
	let audio_chunks: Blob[] = [];
	let module_promises: [
		Promise<typeof import("extendable-media-recorder")>,
		Promise<typeof import("extendable-media-recorder-wav-encoder")>
	];

	function get_modules(): void {
		module_promises = [
			import("extendable-media-recorder"),
			import("extendable-media-recorder-wav-encoder")
		];
	}

	if (streaming) {
		get_modules();
	}

	const dispatch = createEventDispatcher<{
		change: FileData | null;
		stream: FileData;
		edit: never;
		play: never;
		pause: never;
		stop: never;
		end: never;
		drag: boolean;
		error: string;
		upload: FileData;
		clear: undefined;
		start_recording: undefined;
		pause_recording: undefined;
		stop_recording: FileData | null;
	}>();

	const dispatch_blob = async (
		blobs: Uint8Array[] | Blob[],
		event: "stream" | "change" | "stop_recording"
	): Promise<void> => {
		let _audio_blob = new File(blobs, "audio.wav");
		const val = await prepare_files([_audio_blob], event === "stream");
		value = ((await upload(val, root))?.filter(Boolean) as FileData[])[0];
		dispatch(event, value);
	};

	onDestroy(() => {
		if (streaming && recorder && recorder.state !== "inactive") {
			recorder.stop();
		}
	});

	async function handle_chunk(event: IBlobEvent): Promise<void> {
		let buffer = await event.data.arrayBuffer();
		let payload = new Uint8Array(buffer);
		if (!header) {
			header = new Uint8Array(buffer.slice(0, NUM_HEADER_BYTES));
			payload = new Uint8Array(buffer.slice(NUM_HEADER_BYTES));
		}
		if (pending) {
			pending_stream.push(payload);
		} else {
			let blobParts = [header].concat(pending_stream, [payload]);
			dispatch_blob(blobParts, "stream");
			pending_stream = [];
		}
	}

	$: if (submit_pending_stream_on_pending_end && pending === false) {
		submit_pending_stream_on_pending_end = false;
		if (header && pending_stream) {
			let blobParts: Uint8Array[] = [header].concat(pending_stream);
			pending_stream = [];
			dispatch_blob(blobParts, "stream");
		}
	}

	function clear(): void {
		dispatch("change", null);
		dispatch("clear");
		mode = "";
		value = null;
	}

	function handle_load({ detail }: { detail: FileData }): void {
		value = detail;
		dispatch("change", detail);
		dispatch("upload", detail);
	}
</script>

<AudioRecorder
	bind:mode
	{i18n}
	{dispatch}
	{dispatch_blob}
	{waveform_settings}
	{handle_reset_value}
/>
