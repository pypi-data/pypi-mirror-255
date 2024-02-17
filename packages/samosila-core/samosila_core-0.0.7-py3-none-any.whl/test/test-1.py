from typing import Any, Dict

from openserver.types import (BaseLLM, CallbackManager, CallbackHandler, Callbacks,
                                   LLmInputInterface, ManipulationManager, Manipulations, ManipulationHandler)


class ExampleCallback(CallbackHandler):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_llm_start(self, **kwargs):
        print("LLM Start")

    def on_llm_end(self, **kwargs):
        print("LLM End")


class ExampleManipulation(ManipulationHandler):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_llm_start(self, data, **kwargs):
        data['hello'] = 'bye'
        return data


class ExampleLLM(BaseLLM):

    def __init__(self, configs: LLmInputInterface, callback_manager: CallbackManager, manipulation_manager: ManipulationManager | None = None):
        super().__init__(configs, callback_manager, manipulation_manager)

    def completion(self, manipulations: Manipulations = None, callbacks: Callbacks = None, metadata: Dict[str, Any] | None = None, **kwargs):

        self.callback_manager.on_llm_start(callbacks)

        print("response")

        if self.manipulation_manager:
          print(self.manipulation_manager.on_llm_start(
              {'hello': 'world'}, manipulations))

        self.callback_manager.on_llm_end(callbacks)

        return ""


callback_manager = CallbackManager([ExampleCallback()])
manipulation_manager = ManipulationManager([ExampleManipulation()])
configs = LLmInputInterface(llm_name='')

llm = ExampleLLM(configs, callback_manager, manipulation_manager)

llm.completion()
