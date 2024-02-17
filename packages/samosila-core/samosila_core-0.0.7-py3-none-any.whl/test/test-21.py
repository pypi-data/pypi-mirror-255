import json
import types
from typing import Any, List, Literal, Type, TypeVar
from string import Formatter
from pydantic import BaseModel
from inspect import FrameInfo, currentframe, getouterframes

from samosila.core import (
    CompleteInput, UserMessage, ParserManipulationHandler,
    ManipulationManager, CallbackManager, OpenAIProvider,
    BaseMessage, ProviderBase, PydanticOpenAIOutputParser,
    ParserOptions, PydanticOutputParser, PydanticFuncParser,
    FunctionCall, TogetherProvider
)













class Recipe(BaseModel):
    name: str
    ingredients: list[str]
    instructions: list[str]
    duration: int
    duration_metric: str


# parser = PydanticOutputParser(Recipe)

# print(parser.get_format_instructions() + "\n\n")
# print(parser.parse("""{
# "ingredients": ["ham", "turkey", "stuffing", "gravy", "mashed potatoes", "green beans", "pumpkin pie"],
# "instructions": ["prepare the ham", "cook the turkey", "make the stuffing", "prepare the gravy", "mash the potatoes", "steam the green beans", "bake the pumpkin pie"],
# "duration": 210,
# "duration_metric": "minutes"
# }""").duration, "\n\n")


callback_manager = CallbackManager([])
manipulation_manager = ManipulationManager([])

# configs = CompleteInput(
#     provider_model='gpt-3.5-turbo',
#     api_key='',
#     completion_response="""{
#  "ingredients": ["ham", "turkey", "stuffing", "gravy", "mashed potatoes", "green beans", "pumpkin pie"],
#  "instructions": ["prepare the ham", "cook the turkey", "make the stuffing", "prepare the gravy", "mash the potatoes", "steam the green beans", "bake the pumpkin pie"],
#  "duration": 210,
#  "duration_metric": "minutes"
#  }"""
# )

# if res is not None:
#     print("\n\n")
#     print(res.metadata["parsed_response"].final_result)
#     print("\n")
#     print(res.metadata["parsed_response"].final_result.ingredients)
#     print("\n")
#     print(res.metadata["parsed_response"].final_result.duration)

configs = CompleteInput(
    # provider_model='nousresearch/nous-capybara-7b',
    # base_url="https://openrouter.ai/api/v1",
    # api_key='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',

    # provider_model="gpt-3.5-turbo",
    # api_key="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"
    
    provider_model="gpt-3.5-turbo",
    api_key="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"
)


# LLM Initialize ( Parsers )

# Chain (System, Context, LLM, Instruction, Inputs, Response Format)

# Diffrent Methods (With Function or Manual) -
# Diffrent Providers (General - Llamcpp Gramers - OpenAI - Nexus Raven)
# -> Diffrent Function for Chain Creation and Messages and ..
# Diffrent Parsers (Bool - Enum - Pydantic)


llm = TogetherProvider(configs, callback_manager, manipulation_manager)
# llm = OpenAIProvider(configs, callback_manager, manipulation_manager)
# res = llm.chat([UserMessage(content="Hello")], configs=configs.model_copy(update={
#     "temperature": 0.2,
#     "max_tokens": 1000,
#     "top_p": 1,
# }))


def generate_recipe(topic: str) -> Recipe:
    """
    Generate a recipe for a given topic.
    """
    return chain(llm, configs=ChainConfig(chain_type="pydantic", llm_type="openai", input_type="function"))  # <- this is doing all the magic


# generate llm response
recipe = generate_recipe("christmas dinner")

print(recipe.duration)
