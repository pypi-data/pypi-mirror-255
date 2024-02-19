# gradio_gradioworkbook

A Custom Gradio component to build AI Notebooks powered by AIConfig.

## Example usage

Please see the demo/app.py for full details, but generally all you need to do
is add these lines to your component:

```python
import gradio as gr
from gradio_gradioworkbook import GradioWorkbook

AICONFIG_FILE_PATH = "./example_aiconfig.json" #Can also be empty or None!
with gr.Blocks() as demo:
    GradioWorkbook(filepath=AICONFIG_FILE_PATH)

demo.queue().launch()
```

For the remaining commands for local development, please follow the
instructions from the `README-dev.md` file!
