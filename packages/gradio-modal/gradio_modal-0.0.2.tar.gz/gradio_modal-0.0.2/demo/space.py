
import gradio as gr
from app import demo as app
import os

_docs = {'Modal': {'description': 'Modal is a layout element within Blocks that will show its content in a popup above other content.\n    from gradio_modal import Modal\n    with gr.Blocks() as demo:\n        with Modal():\n            text1 = gr.Textbox()\n            text2 = gr.Textbox()\n            btn = gr.Button("Button")', 'members': {'__init__': {'visible': {'type': 'bool', 'default': 'False', 'description': 'If False, modal will be hidden.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional string or list of strings that are assigned as the class of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'allow_user_close': {'type': 'bool', 'default': 'True', 'description': 'If True, user can close the modal (by clicking outside, clicking the X, or the escape key).'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.'}}, 'postprocess': {}}, 'events': {'blur': {'type': None, 'default': None, 'description': 'This listener is triggered when the Modal is unfocused/blurred.'}}}, '__meta__': {'additional_interfaces': {}}}
    
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
# `gradio_modal`

<div style="display: flex; gap: 7px;">
<a href="https://pypi.org/project/gradio_modal/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_modal"></a>  
</div>

A popup modal component
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_modal
```

## Usage

```python
import gradio as gr
from gradio_modal import Modal

with gr.Blocks() as demo:
    with gr.Tab("Tab 1"):
        text_1 = gr.Textbox(label="Input 1")
        text_2 = gr.Textbox(label="Input 2")
        text_1.submit(lambda x:x, text_1, text_2)
        show_btn = gr.Button("Show Modal")
        gr.Examples(
            [["Text 1", "Text 2"], ["Text 3", "Text 4"]],
            inputs=[text_1, text_2],
        )
    with gr.Tab("Tab 2"):
        gr.Markdown("This is tab 2")
    with Modal(visible=False) as modal:
        gr.Markdown("Hello world!")
    show_btn.click(lambda: Modal(visible=True), None, modal)

if __name__ == "__main__":
    demo.launch()

```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `Modal`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["Modal"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["Modal"]["events"], linkify=['Event'])







    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {};
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
