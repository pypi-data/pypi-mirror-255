import time
import requests
from typing import Any, Dict, List, Literal, Optional

from ..utils import image_to_base64

from ..types import (
    CallbackManager, Callbacks, ImageContent,
    ProviderBase, ManipulationManager,
    Manipulations, NovitaInput,
    image_generation_decorator, ImageData
)

class NovitaProvider(ProviderBase):

    def __init__(self, configs: NovitaInput, callback_manager: CallbackManager, manipulation_manager: ManipulationManager | None = None):
        self.model_validate(configs)
        super().__init__(configs, callback_manager, manipulation_manager)
        self.configs: NovitaInput = configs

    @classmethod
    def model_validate(cls, configs: NovitaInput):
        try:
            from novita_client import NovitaClient
        except ImportError as e:
            raise ImportError(
                "Could not import novita python package. "
                "Please install it with `pip install novita_client`."
            ) from e

        cls.client = NovitaClient(configs.api_key)

    @image_generation_decorator
    def image_generation(
        self,
        prompt: str,
        size: Literal['256x256', '512x512', '1024x1024', '1792x1024', '1024x1792'],
        data: Optional[ImageData] = None,
        configs: Optional[NovitaInput] = None,
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
            from novita_client import Txt2ImgRequest, save_image

            width, height = data.size.split('x')
            progress = self.client.sync_txt2img(
                request=Txt2ImgRequest(
                    prompt=data.prompt,
                    negative_prompt=data.negative_prompt or "",
                    model_name=data.configs.provider_model,
                    sampler_name=data.configs.sampler_name,
                    batch_size=data.configs.n,
                    n_iter=1,
                    steps=data.steps or 20,
                    cfg_scale=data.configs.cfg,
                    height=int(width),
                    width=int(height)
                ),
                download_images=True if data.response_format == "b64_json" else False
            )
            if progress.data is not None:
                data.response = []
                if progress.data.imgs_bytes is not None:
                    if data.download_path is not None:
                        for i, img_bytes in enumerate(progress.data.imgs_bytes):
                            if progress.data.imgs is not None:
                                save_image(
                                    img_bytes, data.download_path.format(image=progress.data.imgs[i].split("/")[-1]))
                    for img_bytes in progress.data.imgs_bytes:
                        data.response.append(ImageContent(b64_json=str(img_bytes)))
                elif progress.data.imgs is not None:
                    for img in progress.data.imgs:
                        data.response.append(ImageContent(url=img))

            return data
        except Exception as e:
            raise e

    def img2img(self, data: ImageData, images: List[str]):
        try:
            from novita_client import Img2ImgRequest, save_image

            width, height = data.size.split('x')
            progress = self.client.sync_img2img(
                request=Img2ImgRequest(
                    prompt=data.prompt,
                    negative_prompt=data.negative_prompt or "",
                    model_name=data.configs.provider_model,
                    sampler_name=data.configs.sampler_name,
                    batch_size=data.configs.n,
                    n_iter=1,
                    steps=data.steps,
                    cfg_scale=data.configs.cfg,
                    height=int(width),
                    width=int(height),
                    init_images=[image_to_base64(img) for img in images]
                ),
                download_images=False if data.download_path is None else True
            )
            if progress.data is not None:
                if progress.data.imgs_bytes is not None:
                    for i, img_bytes in enumerate(progress.data.imgs_bytes):
                        if progress.data.imgs is not None:
                            save_image(
                                img_bytes, f'{progress.data.imgs[i].split("/")[-1]}')
                return progress.data.imgs
        except Exception as e:
            raise e

    def search_models(self, attribute: str, value: Any):
        models = self.client.models() if self.models is None else self.models
        self.models = models
        return [model for model in models if self.filter_models(model, attribute, value)]

    def all_models(self):
        models = self.client.models() if self.models is None else self.models
        self.models = models
        return models

    def filter_models(self, model: Any, attribute: str, value: Any) -> bool:
        if attribute in ["name", "sd_name", "base_model", "civitai_tags", "download_name"]:
            field = getattr(model, attribute)
            if field is None:
                return False
            return field.find(value) != -1
        if attribute in ["civitai_version_id", "download_status"]:
            field = getattr(model, attribute)
            if field is None:
                return False
            return field == value
        return False

    def upscale_image(self, image_path: str):
        from novita_client import UpscaleRequest

        progress = self.client.upscale(request=UpscaleRequest(
            image=image_to_base64(image_path)
        ))

        if progress.data is not None:
            return self.retry_request(progress.data.task_id)

    def retry_request(self, task_id):
        delay = 1  # initial delay
        max_delay = 4  # maximum delay
        url = f"https://api.novita.ai/v2/progress?task_id={task_id}"
        headers = {
            'X-Omni-Key': self.configs.api_key
        }

        while delay <= max_delay:
            time.sleep(delay)
            progress_response = requests.get(url, headers=headers).json()

            if progress_response["data"] is None or progress_response["data"]['status'] == 1 and progress_response["data"]['progress'] < 1:
                delay *= 2  # double the delay
            else:
                return progress_response["data"]["imgs"]

        # If we've made it here, we've failed all attempts
        raise Exception(
            "Failed to get a successful response after multiple attempts")
