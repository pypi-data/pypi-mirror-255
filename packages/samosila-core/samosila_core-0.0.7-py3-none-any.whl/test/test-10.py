import torch
from lavis.models import load_model_and_preprocess

from openserver.utils.image import load_image

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

raw_image = load_image("QtxgNsmJQSs.jpg").convert("RGB")

model, vis_processors, _ = load_model_and_preprocess(
    name="blip_caption", model_type="base_coco", is_eval=True, device=device)

image = vis_processors["eval"](raw_image).unsqueeze(0).to(device)
# generate caption
model.generate({"image": image})
# ['a large fountain spewing water into the air']
