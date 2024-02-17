import base64
import time
import requests
from typing import Any, Dict, Literal, Optional


from ..utils.image import base64_to_image
from ..types import (
    CallbackManager, Callbacks, ImageContent,
    ProviderBase, ManipulationManager,
    Manipulations, SegmindInput,
    image_generation_decorator, ImageData
)


class SegmindProvider(ProviderBase):

    def __init__(self, configs: SegmindInput, callback_manager: CallbackManager, manipulation_manager: ManipulationManager | None = None):
        self.model_validate()
        super().__init__(configs, callback_manager, manipulation_manager)
        self.configs: SegmindInput = configs

    @classmethod
    def model_validate(cls):
        pass

    @image_generation_decorator
    def image_generation(
        self,
        prompt: str,
        size: Literal['256x256', '512x512', '1024x1024', '1792x1024', '1024x1792'],
        data: Optional[ImageData] = None,
        configs: Optional[SegmindInput] = None,
        negative_prompt: Optional[str] = None,
        steps: Optional[int] = None,
        manipulations: Manipulations = None,
        callbacks: Callbacks = None,
        metadata: Dict[str, Any] = {},
    ):
        try:
            if data is None:
                raise Exception("Decorator didnt Initialized Data")
            data = self.image_generations(data, callbacks)
            return data
        except Exception as e:
            raise e

    def image_generations(self, data: ImageData, callbacks):
        try:
            width, height = data.size.split('x')

            url = f"https://api.segmind.com/v1/{data.configs.provider_model}"
            _data = {
                "prompt": data.prompt,
                "negative_prompt": data.negative_prompt,
                "samples": data.configs.n,  # type: ignore
                "scheduler": data.configs.sampler_name,
                "num_inference_steps": data.steps,
                "guidance_scale": data.configs.cfg,
                "img_width": width,
                "img_height": height,
                "base64": True if data.response_format == "b64_json" else False
            }

            response = requests.post(url, json=_data, headers={
                'x-api-key': data.configs.api_key or ""
            })
            if response.content is not None:
                image = base64.b64encode(response.content).decode('utf-8')
                if data.download_path is not None:
                    base64_to_image(image, data.download_path.format(
                        image=f"output-{time.time()}"))
                data.response = [ImageContent(b64_json=image)]

            return data
        except Exception as e:
            raise e
