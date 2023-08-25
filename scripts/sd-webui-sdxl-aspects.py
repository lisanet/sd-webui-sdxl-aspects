import gradio as gr
from modules.ui_components import FormRow
import modules.scripts as scripts
from modules import images
from modules.shared import opts


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
            with FormRow():
                crop = gr.Checkbox(label="Crop to fit aspect ratio", value=False, elem_id=f'{tab}_sdxl_aspect_crop')
                overwrite = gr.Checkbox(label="Overwrite uncropped image", value=False, elem_id=f'{tab}_sdxl_aspect_overwrite')
            gr.Markdown()
        slider.change(self.get_aspect, inputs=[slider], outputs=[ar, self.dims_w, self.dims_h], show_progress=False)
        
        return [slider, ar, crop, overwrite]


    def crop_image(self, img):
        w = img.width
        h = img.height
        ar_w = self.ar_w
        ar_h = self.ar_h
        # if orientation is different, switch aspect ratio
        if (w - h) * (self.ar_w - self.ar_h) < 0:
            ar_w = self.ar_h
            ar_h = self.ar_w
            
        # calc new size to match aspect, round to nearest even num. 
        # This will give exakt pixel aspect ratios, 
        # except for 3:2 and 16:9 where the difference is 0.66 pixels in only one dimension :-)
        if w / ar_w * ar_h > h:
            crop_w = int((h / ar_h * ar_w + 1)/2) * 2
            crop_h = h
        else:
            crop_w = w
            crop_h = int((w / ar_w * ar_h + 1)/2) * 2

        top = (h - crop_h) / 2
        left = (w - crop_w) / 2
        bottom = top + crop_h
        right = left + crop_w 
        return img.crop((left, top, right, bottom ))


    def process(self, p, slider, ar, crop, overwrite):
        if crop:
            p.extra_generation_params["Ascpet ratio"] = ar
            p.extra_generation_params["Ascpet ratio crop"] = crop
            if overwrite:
                p.do_not_save_samples = True


    def postprocess(self, p, processed, slider, ar, crop, overwrite):
        if crop:
            count = len(processed.images)
            index = 0
            self.get_aspect(slider)
            unwanted_grid = count < 2 and opts.grid_only_if_multiple
            
            for i in range(count):
                if i == 0 and not p.do_not_save_grid and not unwanted_grid: # skip grid
                    continue

                processed.images[i] = self.crop_image(processed.images[i])
                suffix = "" if overwrite else "-crop"
                img_info = processed.infotext(p, index)
                images.save_image(processed.images[i], p.outpath_samples, "",
                   processed.seed + index, processed.prompt, opts.samples_format, info = img_info, p = p, suffix = suffix)
                index += 1


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
