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
