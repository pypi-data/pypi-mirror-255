
# `gradio_modal`
<a href="https://pypi.org/project/gradio_modal/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_modal"></a>  

A popup modal component

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

## `Modal`

### Initialization

<table>
<thead>
<tr>
<th align="left">name</th>
<th align="left" style="width: 25%;">type</th>
<th align="left">default</th>
<th align="left">description</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left"><code>visible</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If False, modal will be hidden.</td>
</tr>

<tr>
<td align="left"><code>elem_id</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>elem_classes</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional string or list of strings that are assigned as the class of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>allow_user_close</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True, user can close the modal (by clicking outside, clicking the X, or the escape key).</td>
</tr>

<tr>
<td align="left"><code>render</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.</td>
</tr>
</tbody></table>


### Events

| name | description |
|:-----|:------------|
| `blur` | This listener is triggered when the Modal is unfocused/blurred. |



