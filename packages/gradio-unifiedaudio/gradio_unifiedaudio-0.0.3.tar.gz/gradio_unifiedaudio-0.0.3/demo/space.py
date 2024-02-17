
import gradio as gr
from app import demo as app
import os

_docs = {'UnifiedAudio': {'description': 'Creates an audio component that can be used to upload/record audio (as an input) or display audio (as an output).', 'members': {'__init__': {'value': {'type': 'str\n    | pathlib.Path\n    | tuple[int, numpy.ndarray]\n    | Callable\n    | None', 'default': 'None', 'description': 'A path, URL, or [sample_rate, numpy array] tuple (sample rate in Hz, audio data as a float or int numpy array) for the default value that UnifiedAudio component is going to take. If callable, the function will be called whenever the app loads to set the initial value of the component.'}, 'image': {'type': 'str | None', 'default': 'None', 'description': 'A path or URL to an image to display above the audio component. If None, no image will be displayed.'}, 'sources': {'type': 'list["upload" | "microphone"] | None', 'default': 'None', 'description': 'A list of sources permitted for audio. "upload" creates a box where user can drop an audio file, "microphone" creates a microphone input. The first element in the list will be used as the default source. If None, defaults to ["upload", "microphone"], or ["microphone"] if `streaming` is True.'}, 'type': {'type': '"numpy" | "filepath"', 'default': '"numpy"', 'description': 'The format the audio file is converted to before being passed into the prediction function. "numpy" converts the audio to a tuple consisting of: (int sample rate, numpy.array for the data), "filepath" passes a str path to a temporary file containing the audio.'}, 'label': {'type': 'str | None', 'default': 'None', 'description': 'The label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.'}, 'every': {'type': 'float | None', 'default': 'None', 'description': "If `value` is a callable, run the function 'every' number of seconds while the client connection is open. Has no effect otherwise. Queue must be enabled. The event can be accessed (e.g. to cancel it) via this component's .load_event attribute."}, 'show_label': {'type': 'bool | None', 'default': 'None', 'description': 'if True, will display label.'}, 'container': {'type': 'bool', 'default': 'True', 'description': 'If True, will place the component in a container - providing some extra padding around the border.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'relative width compared to adjacent Components in a Row. For example, if Component A has scale=2, and Component B has scale=1, A will be twice as wide as B. Should be an integer.'}, 'min_width': {'type': 'int', 'default': '160', 'description': 'minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.'}, 'interactive': {'type': 'bool | None', 'default': 'None', 'description': 'if True, will allow users to upload and edit a audio file; if False, can only be used to play audio. If not provided, this is inferred based on whether the component is used as an input or output.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, component will be hidden.'}, 'streaming': {'type': 'bool', 'default': 'False', 'description': 'If set to True when used in a `live` interface as an input, will automatically stream webcam feed. When used set as an output, takes audio chunks yield from the backend and combines them into one streaming audio output.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.'}, 'format': {'type': '"wav" | "mp3"', 'default': '"wav"', 'description': 'The file format to save audio files. Either \'wav\' or \'mp3\'. wav files are lossless but will tend to be larger files. mp3 files tend to be smaller. Default is wav. Applies both when this component is used as an input (when `type` is "format") and when this component is used as an output.'}, 'autoplay': {'type': 'bool', 'default': 'False', 'description': 'Whether to automatically play the audio when the component is used as an output. Note: browsers will not autoplay audio files if the user has not interacted with the page yet.'}, 'show_share_button': {'type': 'bool | None', 'default': 'None', 'description': 'If True, will show a share icon in the corner of the component that allows user to share outputs to Hugging Face Spaces Discussions. If False, icon does not appear. If set to None (default behavior), then the icon appears if this Gradio app is launched on Spaces, but not otherwise.'}, 'min_length': {'type': 'int | None', 'default': 'None', 'description': 'The minimum length of audio (in seconds) that the user can pass into the prediction function. If None, there is no minimum length.'}, 'max_length': {'type': 'int | None', 'default': 'None', 'description': 'The maximum length of audio (in seconds) that the user can pass into the prediction function. If None, there is no maximum length.'}, 'waveform_options': {'type': 'WaveformOptions | None', 'default': 'None', 'description': 'A dictionary of options for the waveform display. Options include: waveform_color (str), waveform_progress_color (str), show_controls (bool), skip_length (int). Default is None, which uses the default values for these options.'}}, 'postprocess': {'value': {'type': 'tuple[int, numpy.ndarray]\n    | str\n    | pathlib.Path\n    | bytes\n    | None', 'description': 'audio data in either of the following formats: a tuple of (sample_rate, data), or a string filepath or URL to an audio file, or None.'}}, 'preprocess': {'return': {'type': 'tuple[int, numpy.ndarray] | str | None', 'description': None}, 'value': None}}, 'events': {'stream': {'type': None, 'default': None, 'description': 'This listener is triggered when the user streams the UnifiedAudio.'}, 'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the UnifiedAudio changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'clear': {'type': None, 'default': None, 'description': 'This listener is triggered when the user clears the UnifiedAudio using the X button for the component.'}, 'play': {'type': None, 'default': None, 'description': 'This listener is triggered when the user plays the media in the UnifiedAudio.'}, 'pause': {'type': None, 'default': None, 'description': 'This listener is triggered when the media in the UnifiedAudio stops for any reason.'}, 'stop': {'type': None, 'default': None, 'description': 'This listener is triggered when the user reaches the end of the media playing in the UnifiedAudio.'}, 'start_recording': {'type': None, 'default': None, 'description': 'This listener is triggered when the user starts recording with the UnifiedAudio.'}, 'pause_recording': {'type': None, 'default': None, 'description': 'This listener is triggered when the user pauses recording with the UnifiedAudio.'}, 'stop_recording': {'type': None, 'default': None, 'description': 'This listener is triggered when the user stops recording with the UnifiedAudio.'}, 'upload': {'type': None, 'default': None, 'description': 'This listener is triggered when the user uploads a file into the UnifiedAudio.'}}}, '__meta__': {'additional_interfaces': {'WaveformOptions': {'source': 'class WaveformOptions(TypedDict, total=False):\n    waveform_color: str\n    waveform_progress_color: str\n    show_controls: bool\n    skip_length: int'}}, 'user_fn_refs': {'UnifiedAudio': []}}}
    
abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_unifiedaudio`

<div style="display: flex; gap: 7px;">
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.2%20-%20orange">  
</div>

Python library for easily interacting with trained machine learning models
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_unifiedaudio
```

## Usage

```python

import gradio as gr
from gradio_unifiedaudio import UnifiedAudio
from os.path import abspath, join, pardir
from pathlib import Path

example = UnifiedAudio().example_inputs()
dir_ = Path(__file__).parent

def test_mic(audio):
    return UnifiedAudio(value=audio)

with gr.Blocks() as demo:
    mic = UnifiedAudio(sources="microphone")
    mic.change(test_mic, mic, mic)

if __name__ == '__main__':
    demo.launch()

```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `UnifiedAudio`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["UnifiedAudio"]["members"]["__init__"], linkify=['WaveformOptions'])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["UnifiedAudio"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function. 
- When used as an output, the component only impacts the return signature of the user function. 

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As output:** Should return, audio data in either of the following formats: a tuple of (sample_rate, data), or a string filepath or URL to an audio file, or None.

 ```python
def predict(
    value: tuple[int, numpy.ndarray] | str | None
) -> tuple[int, numpy.ndarray]
    | str
    | pathlib.Path
    | bytes
    | None:
    return value
```
""", elem_classes=["md-custom", "UnifiedAudio-user-fn"], header_links=True)




    code_WaveformOptions = gr.Markdown("""
## `WaveformOptions`
```python
class WaveformOptions(TypedDict, total=False):
    waveform_color: str
    waveform_progress_color: str
    show_controls: bool
    skip_length: int
```""", elem_classes=["md-custom", "WaveformOptions"], header_links=True)

    demo.load(None, js=r"""function() {
    const refs = {
            WaveformOptions: [], };
    const user_fn_refs = {
          UnifiedAudio: [], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
        
        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
