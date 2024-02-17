from dotenv import load_dotenv
from openserver.core.image_providers.base import ImageInputInterface
from openserver.core.image_providers.novita import NovitaImageModel

load_dotenv()

image_model_provider = NovitaImageModel()

# res = image_model_provider.txt2img(ImageInputInterface(
#     prompt = "A cyan haired man on vacation enjoying the local party scene  at dawn in Mos Eisley on the planet Tatooine in Star Wars , a look of terror scared horrified , futuristic Neon cyberpunk synthwave cybernetic  Robert Hagan and by Naoko Takeuchi",
#     negative_prompt = "(nsfw nudity naked nipples:1.3)",
#     model = "dynavisionXLAllInOneStylized_release0534bakedvae_129001.safetensors",
#     sampler_name="DPM++ 2M Karras",
#     n = 1,
#     steps = 20,
#     cfg = 7,
#     seed = 3223553976,
#     size="512x512",
#     api_key="d734a50e-0fc4-4de0-8b9b-e2a6acafc302"
# ))

# print(res)

models = image_model_provider.search_models(
    attribute="sd_name", value="dynavisionXL")

print(models)