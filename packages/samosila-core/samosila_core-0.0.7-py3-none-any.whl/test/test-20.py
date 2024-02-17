from samosila.core import (
    FakeProvider, CallbackManager, CompleteInput, ManipulationManager
)

callback_manager = CallbackManager([])
manipulation_manager = ManipulationManager([])
configs = CompleteInput(provider_model="edge_tts", api_key="")

text = "Born and raised in the charming south, I can add a touch of sweet southern hospitality to your audiobooks and podcasts"

tts = FakeProvider(
    configs,
    callback_manager,
    manipulation_manager
)


res = tts.completion(text)

print(res)
