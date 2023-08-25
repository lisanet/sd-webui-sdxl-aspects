import gradio as gr
from modules.ui_components import FormRow
import modules.scripts as scripts


class AspectScript(scripts.Script):
    def __init__(self):
        super().__init__()
        self.aspect_types = {
            0: ["1 : 1", 1024, 1024],
            1: ["2 : 3", 832, 1216],
            2: ["3 : 4", 896, 1152],
            3: ["4 : 5", 896, 1152],
            4: ["16 : 9", 1344, 768],
            5: ["21 : 9", 1536, 640],
            6: ["2.35 : 1", 1536, 640]
        }
        self.w = 1024
        self.h = 1024
        self.ar_w = 1
        self.ar_h = 1
        self.dims_w = None
        self.dims_h = None

    def title(self):
        return "SDXL Aspect Crop"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def get_aspect(self, x):
        [text, w, h] = self.aspect_types.get(x)
        self.ar_w, self.ar_h = text.split(":")
        self.ar_w = float(self.ar_w)
        self.ar_h = float(self.ar_h)
        return text, w, h


    def ui(self, is_img2img):
        tab = elem_id=f'{"img" if is_img2img else "txt"}2img'
        with gr.Column(elem_id=f'{tab}_container_sdxl_aspect'):
            gr.Markdown()
            with FormRow():
                with gr.Column(scale=4):
                    slider = gr.Slider(0, 6, step=1, label="Aspect type", elem_id=f'{tab}_sdxl_aspect_type')
                with gr.Column(min_width=50, scale=1):
                    ar = gr.Textbox("1:1", label="Aspect ratio", show_label=True, interactive=False, elem_id=f'{tab}_sdxl_aspect_ar')
            gr.Markdown()
        slider.change(self.get_aspect, inputs=[slider], outputs=[ar, self.dims_w, self.dims_h], show_progress=False)

        return [slider, ar]


    # https://github.com/AUTOMATIC1111/stable-diffusion-webui/pull/7456#issuecomment-1414465888
    def after_component(self, component, **kwargs):
        if kwargs.get("elem_id") == "txt2img_width":
            self.dims_w = component
        if kwargs.get("elem_id") == "txt2img_height":
            self.dims_h = component

        if kwargs.get("elem_id") == "img2img_width":
            self.dims_w = component
        if kwargs.get("elem_id") == "img2img_height":
            self.dims_h = component
