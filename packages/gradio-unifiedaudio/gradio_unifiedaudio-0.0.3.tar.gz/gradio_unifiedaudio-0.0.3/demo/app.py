
import gradio as gr
from gradio_unifiedaudio import UnifiedAudio
from os.path import abspath, join, pardir
from pathlib import Path

example = UnifiedAudio().example_inputs()
dir_ = Path(__file__).parent

def test_mic(audio):
    return UnifiedAudio(value=audio, image="demo/freeman.jpg")

def clear(audio):
    return UnifiedAudio(value=None)

with gr.Blocks() as demo:
    mic = UnifiedAudio(sources="microphone")
    mic.change(test_mic, mic, mic)
    mic.end(clear, mic, mic)

if __name__ == '__main__':
    demo.launch()
