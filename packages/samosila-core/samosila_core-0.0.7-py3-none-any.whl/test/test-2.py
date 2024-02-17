from dotenv import load_dotenv
from openserver.providers.gf4 import FreeProvider
from openserver.providers.fake import FakeProvider

from openserver.types import (
    CallbackManager, CallbackHandler, CompleteInput, ManipulationManager, ManipulationHandler
)
from openserver.types.base import FeaturesState

load_dotenv()


class ExampleCallback(CallbackHandler):

    def __init__(self, features_state: FeaturesState = FeaturesState(), **kwargs):
        super().__init__(features_state, **kwargs)
        pass

    def on_llm_start(self, data, **kwargs):
        print("LLM Start")

    def on_llm_end(self, data, **kwargs):
        print("LLM End")

    def on_llm_new_token(self, token: str, **kwargs):
        print(token)


class ExampleCallback2(CallbackHandler):

    def __init__(self, features_state: FeaturesState = FeaturesState(), **kwargs):
        super().__init__(features_state, **kwargs)
        pass

    def on_llm_start(self, data, **kwargs):
        print("LLM Start 2")

    def on_llm_end(self, data, **kwargs):
        print("LLM End 2")

    def on_llm_new_token(self, token: str, **kwargs):
        print(token)


class ExampleManipulation(ManipulationHandler):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_llm_start(self, data, **kwargs):
        data.prompt.content = 'sample changing prompt'
        return data


callback_manager = CallbackManager([
    ExampleCallback(features_state=FeaturesState(on_llm_new_token=False)),
    ExampleCallback2(features_state=FeaturesState(on_llm_start=False))
])
manipulation_manager = ManipulationManager([])
# configs = CompleteInput(provider_model='NousResearch/Nous-Capybara-7B-V1p9')
# configs = CompleteInput(provider_model='models/text-bison-001', streaming=True)
# configs = CompleteInput(provider_model='models/chat-bison-001', streaming=True)
# configs = CompleteInput(
#     provider_model='mistralai/mixtral-8x7b-instruct', base_url="https://openrouter.ai/api/v1", api_key="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")
# configs = CompleteInput(
#     provider_model='D:/AI/llama.cpp/models/minichat-1.5-3b.q6_k.gguf', n_gpu_layers=40, streaming=True)
configs = CompleteInput(provider_model='gpt-3.5-turbo', api_key='',  streaming=True)
# configs = CompleteInput(
#     provider_model='accounts/fireworks/models/llama-v2-7b-chat', api_key="enqrbHVOcnDk6BXXTRhpFjxAIFLwmdyzIdbRQ8vbSbuDLGcG")
# configs = CompleteInput(
#     provider_model='command', api_key="CbMuLJILdo1UTkqNfcwDLlw9BtS1n5VKR8CLkTOb")
# configs = CompleteInput(
#     provider_model='gpt-3.5-turbo', base_url="https://neuroapi.host", api_key="sk-zGRW7yRI4zCSjh9E8197B71d7bFa40C4A960272f1932CcFd")

# llm = CohereProvider(configs, callback_manager, manipulation_manager)
# llm = FireworksProvider(configs, callback_manager, manipulation_manager)
# llm = LlamacppProvider(configs, callback_manager, manipulation_manager)
# llm = FreeProvider(configs, callback_manager, manipulation_manager)
# llm = OpenAIProvider(configs, callback_manager, manipulation_manager)
# llm = GoogleGenAIProvider(configs, callback_manager, manipulation_manager)
# llm = TogetherProvider(configs, callback_manager, manipulation_manager)
llm = FakeProvider(configs, callback_manager, manipulation_manager)
res = llm.completion("tell me a joke")
# res = llm.chat([UserMessage(content="tell me a joke")])
print(res)
