# +-----------------------------------------------+
# |                                               |
# |           Give Feedback / Get Help            |
# | https://github.com/BerriAI/litellm/issues/new |
# |                                               |
# +-----------------------------------------------+
#
#  Thank you users! We ❤️ you! - Krrish & Ishaan

from enum import Enum
from .caching import Cache
from typing import cast, List, Dict, Union, Optional
from .exceptions import (
    AuthenticationError,
    InvalidRequestError,
    RateLimitError,
    ServiceUnavailableError,
    OpenAIError,
    ContextWindowExceededError,
    Timeout,
    APIConnectionError,
    APIError,
    BudgetExceededError
)
from openai.openai_object import OpenAIObject
from openai.error import OpenAIError as OriginalError
from .integrations.litedebugger import LiteDebugger
from .integrations.langfuse import LangFuseLogger
from .integrations.custom_logger import CustomLogger
from .integrations.weights_biases import WeightsBiasesLogger
from .integrations.langsmith import LangsmithLogger
from .integrations.prompt_layer import PromptLayerLogger
from .integrations.llmonitor import LLMonitorLogger
from .integrations.supabase import Supabase
from .integrations.berrispend import BerriSpendLogger
from .integrations.aispend import AISpendLogger
from .integrations.helicone import HeliconeLogger
from .integrations.traceloop import TraceloopLogger
import importlib.metadata
import sys
import dotenv
import json
import traceback
import threading
import subprocess
import os
import litellm
import openai
import itertools
import random
import uuid
import requests
import datetime
import time
import tiktoken
import uuid
import aiohttp
import logging
import asyncio
from tokenizers import Tokenizer
from dataclasses import (
    dataclass,
    field,
)  # for storing API inputs, outputs, and metadata
encoding = tiktoken.get_encoding("cl100k_base")

####### ENVIRONMENT VARIABLES ####################
dotenv.load_dotenv()  # Loading env variables using dotenv
sentry_sdk_instance = None
capture_exception = None
add_breadcrumb = None
posthog = None
slack_app = None
alerts_channel = None
heliconeLogger = None
promptLayerLogger = None
langsmithLogger = None
weightsBiasesLogger = None
customLogger = None
langFuseLogger = None
llmonitorLogger = None
aispendLogger = None
berrispendLogger = None
supabaseClient = None
liteDebuggerClient = None
callback_list: Optional[List[str]] = []
user_logger_fn = None
additional_details: Optional[Dict[str, str]] = {}
local_cache: Optional[Dict[str, str]] = {}
last_fetched_at = None
last_fetched_at_keys = None



def json_schema_type(python_type_name: str):
    """Converts standard python types to json schema types

    Parameters
    ----------
    python_type_name : str
        __name__ of type

    Returns
    -------
    str
        a standard JSON schema type, "string" if not recognized.
    """
    python_to_json_schema_types = {
        str.__name__: "string",
        int.__name__: "integer",
        float.__name__: "number",
        bool.__name__: "boolean",
        list.__name__: "array",
        dict.__name__: "object",
        "NoneType": "null",
    }

    return python_to_json_schema_types.get(python_type_name, "string")


def function_to_dict(input_function):  # noqa: C901
    """Using type hints and numpy-styled docstring,
    produce a dictionnary usable for OpenAI function calling

    Parameters
    ----------
    input_function : function
        A function with a numpy-style docstring

    Returns
    -------
    dictionnary
        A dictionnary to add to the list passed to `functions` parameter of `litellm.completion`
    """
    # Get function name and docstring
    try:
        import inspect
        from numpydoc.docscrape import NumpyDocString
        from ast import literal_eval
    except Exception as e:
        raise e

    name = input_function.__name__
    docstring = inspect.getdoc(input_function)
    numpydoc = NumpyDocString(docstring)
    description = "\n".join([s.strip() for s in numpydoc["Summary"]])

    # Get function parameters and their types from annotations and docstring
    parameters = {}
    required_params = []
    param_info = inspect.signature(input_function).parameters

    for param_name, param in param_info.items():
        if hasattr(param, "annotation"):
            param_type = json_schema_type(param.annotation.__name__)
        else:
            param_type = None
        param_description = None
        param_enum = None

        # Try to extract param description from docstring using numpydoc
        for param_data in numpydoc["Parameters"]:
            if param_data.name == param_name:
                if hasattr(param_data, "type"):
                    # replace type from docstring rather than annotation
                    param_type = param_data.type
                    if "optional" in param_type:
                        param_type = param_type.split(",")[0]
                    elif "{" in param_type:
                        # may represent a set of acceptable values
                        # translating as enum for function calling
                        try:
                            param_enum = str(list(literal_eval(param_type)))
                            param_type = "string"
                        except Exception:
                            pass
                    param_type = json_schema_type(param_type)
                param_description = "\n".join(
                    [s.strip() for s in param_data.desc])

        param_dict = {
            "type": param_type,
            "description": param_description,
            "enum": param_enum,
        }

        parameters[param_name] = dict(
            [(k, v) for k, v in param_dict.items() if isinstance(v, str)]
        )

        # Check if the parameter has no default value (i.e., it's required)
        if param.default == param.empty:
            required_params.append(param_name)

    # Create the dictionary
    result = {
        "name": name,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": parameters,
        },
    }

    # Add "required" key if there are required parameters
    if required_params:
        result["parameters"]["required"] = required_params

    return result

def set_callbacks(callback_list, function_id=None):
    global sentry_sdk_instance, capture_exception, add_breadcrumb, posthog, slack_app, alerts_channel, traceloopLogger, heliconeLogger, aispendLogger, berrispendLogger, supabaseClient, liteDebuggerClient, llmonitorLogger, promptLayerLogger, langFuseLogger, customLogger, weightsBiasesLogger, langsmithLogger
    try:
        for callback in callback_list:
            print_verbose(f"callback: {callback}")
            if callback == "sentry":
                try:
                    import sentry_sdk
                except ImportError:
                    print_verbose(
                        "Package 'sentry_sdk' is missing. Installing it...")
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", "sentry_sdk"]
                    )
                    import sentry_sdk
                sentry_sdk_instance = sentry_sdk
                sentry_trace_rate = (
                    os.environ.get("SENTRY_API_TRACE_RATE")
                    if "SENTRY_API_TRACE_RATE" in os.environ
                    else "1.0"
                )
                sentry_sdk_instance.init(
                    dsn=os.environ.get("SENTRY_DSN"),
                    traces_sample_rate=float(sentry_trace_rate),
                )
                capture_exception = sentry_sdk_instance.capture_exception
                add_breadcrumb = sentry_sdk_instance.add_breadcrumb
            elif callback == "posthog":
                try:
                    from posthog import Posthog
                except ImportError:
                    print_verbose(
                        "Package 'posthog' is missing. Installing it...")
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", "posthog"]
                    )
                    from posthog import Posthog
                posthog = Posthog(
                    project_api_key=os.environ.get("POSTHOG_API_KEY"),
                    host=os.environ.get("POSTHOG_API_URL"),
                )
            elif callback == "slack":
                try:
                    from slack_bolt import App
                except ImportError:
                    print_verbose(
                        "Package 'slack_bolt' is missing. Installing it...")
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", "slack_bolt"]
                    )
                    from slack_bolt import App
                slack_app = App(
                    token=os.environ.get("SLACK_API_TOKEN"),
                    signing_secret=os.environ.get("SLACK_API_SECRET"),
                )
                alerts_channel = os.environ["SLACK_API_CHANNEL"]
                print_verbose(f"Initialized Slack App: {slack_app}")
            elif callback == "traceloop":
                traceloopLogger = TraceloopLogger()
            elif callback == "helicone":
                heliconeLogger = HeliconeLogger()
            elif callback == "llmonitor":
                llmonitorLogger = LLMonitorLogger()
            elif callback == "promptlayer":
                promptLayerLogger = PromptLayerLogger()
            elif callback == "langfuse":
                langFuseLogger = LangFuseLogger()
            elif callback == "wandb":
                weightsBiasesLogger = WeightsBiasesLogger()
            elif callback == "langsmith":
                langsmithLogger = LangsmithLogger()
            elif callback == "aispend":
                aispendLogger = AISpendLogger()
            elif callback == "berrispend":
                berrispendLogger = BerriSpendLogger()
            elif callback == "supabase":
                print_verbose(f"instantiating supabase")
                supabaseClient = Supabase()
            elif callback == "lite_debugger":
                print_verbose(f"instantiating lite_debugger")
                if function_id:
                    liteDebuggerClient = LiteDebugger(email=function_id)
                elif litellm.token:
                    liteDebuggerClient = LiteDebugger(email=litellm.token)
                elif litellm.email:
                    liteDebuggerClient = LiteDebugger(email=litellm.email)
                else:
                    liteDebuggerClient = LiteDebugger(email=str(uuid.uuid4()))
            elif callable(callback):
                customLogger = CustomLogger()
    except Exception as e:
        raise e


# NOTE: DEPRECATING this in favor of using success_handler() in Logging:
def handle_success(args, kwargs, result, start_time, end_time):
    global heliconeLogger, aispendLogger, supabaseClient, liteDebuggerClient, llmonitorLogger
    try:
        model = args[0] if len(args) > 0 else kwargs["model"]
        input = (
            args[1]
            if len(args) > 1
            else kwargs.get("messages", kwargs.get("input", None))
        )
        success_handler = additional_details.pop("success_handler", None)
        failure_handler = additional_details.pop("failure_handler", None)
        additional_details["Event_Name"] = additional_details.pop(
            "successful_event_name", "litellm.succes_query"
        )
        for callback in litellm.success_callback:
            try:
                if callback == "posthog":
                    ph_obj = {}
                    for detail in additional_details:
                        ph_obj[detail] = additional_details[detail]
                    event_name = additional_details["Event_Name"]
                    if "user_id" in additional_details:
                        posthog.capture(
                            additional_details["user_id"], event_name, ph_obj
                        )
                    else:  # PostHog calls require a unique id to identify a user - https://posthog.com/docs/libraries/python
                        unique_id = str(uuid.uuid4())
                        posthog.capture(unique_id, event_name, ph_obj)
                    pass
                elif callback == "slack":
                    slack_msg = ""
                    for detail in additional_details:
                        slack_msg += f"{detail}: {additional_details[detail]}\n"
                    slack_app.client.chat_postMessage(
                        channel=alerts_channel, text=slack_msg
                    )
                elif callback == "helicone":
                    print_verbose("reaches helicone for logging!")
                    model = args[0] if len(args) > 0 else kwargs["model"]
                    messages = args[1] if len(args) > 1 else kwargs["messages"]
                    heliconeLogger.log_success(
                        model=model,
                        messages=messages,
                        response_obj=result,
                        start_time=start_time,
                        end_time=end_time,
                        print_verbose=print_verbose,
                    )
                elif callback == "llmonitor":
                    print_verbose("reaches llmonitor for logging!")
                    model = args[0] if len(args) > 0 else kwargs["model"]

                    input = (
                        args[1]
                        if len(args) > 1
                        else kwargs.get("messages", kwargs.get("input", None))
                    )

                    # if contains input, it's 'embedding', otherwise 'llm'
                    type = "embed" if "input" in kwargs else "llm"

                    llmonitorLogger.log_event(
                        type=type,
                        event="end",
                        model=model,
                        input=input,
                        user_id=kwargs.get("user", "default"),
                        response_obj=result,
                        start_time=start_time,
                        end_time=end_time,
                        run_id=kwargs["litellm_call_id"],
                        print_verbose=print_verbose,
                    )
                elif callback == "langfuse":
                    print_verbose("reaches langfuse for logging!")
                    langFuseLogger.log_event(
                        kwargs=kwargs,
                        response_obj=result,
                        start_time=start_time,
                        end_time=end_time,
                        print_verbose=print_verbose,
                    )

                elif callback == "traceloop":
                    traceloopLogger.log_event(
                        kwargs=kwargs,
                        response_obj=result,
                        start_time=start_time,
                        end_time=end_time,
                        print_verbose=print_verbose,
                    )

                elif callback == "aispend":
                    print_verbose("reaches aispend for logging!")
                    model = args[0] if len(args) > 0 else kwargs["model"]
                    aispendLogger.log_event(
                        model=model,
                        response_obj=result,
                        start_time=start_time,
                        end_time=end_time,
                        print_verbose=print_verbose,
                    )
            except Exception as e:
                # LOGGING
                exception_logging(logger_fn=user_logger_fn, exception=e)
                print_verbose(
                    f"[Non-Blocking] Success Callback Error - {traceback.format_exc()}"
                )
                pass

        if success_handler and callable(success_handler):
            success_handler(args, kwargs)
        pass
    except Exception as e:
        # LOGGING
        exception_logging(logger_fn=user_logger_fn, exception=e)
        print_verbose(
            f"[Non-Blocking] Success Callback Error - {traceback.format_exc()}"
        )
        pass


def completion_with_fallbacks(**kwargs):
    nested_kwargs = kwargs.pop("kwargs", {})
    response = None
    rate_limited_models = set()
    model_expiration_times = {}
    start_time = time.time()
    original_model = kwargs["model"]
    fallbacks = [kwargs["model"]] + nested_kwargs.get("fallbacks", [])
    if "fallbacks" in nested_kwargs:
        # remove fallbacks so it's not recursive
        del nested_kwargs["fallbacks"]
    litellm_call_id = str(uuid.uuid4())

    # max time to process a request with fallbacks: default 45s
    while response == None and time.time() - start_time < 45:
        for model in fallbacks:
            # loop thru all models
            try:
                # check if it's dict or new model string
                # completion(model="gpt-4", fallbacks=[{"api_key": "", "api_base": ""}, {"api_key": "", "api_base": ""}])
                if isinstance(model, dict):
                    kwargs["api_key"] = model.get("api_key", None)
                    kwargs["api_base"] = model.get("api_base", None)
                    model = model.get("model", original_model)
                elif (
                    model in rate_limited_models
                ):  # check if model is currently cooling down
                    if (
                        model_expiration_times.get(model)
                        and time.time() >= model_expiration_times[model]
                    ):
                        rate_limited_models.remove(
                            model
                        )  # check if it's been 60s of cool down and remove model
                    else:
                        continue  # skip model

                # delete model from kwargs if it exists
                if kwargs.get("model"):
                    del kwargs["model"]

                print_verbose(
                    f"trying to make completion call with model: {model}")
                kwargs["litellm_call_id"] = litellm_call_id
                # combine the openai + litellm params at the same level
                kwargs = {**kwargs, **nested_kwargs}
                response = litellm.completion(**kwargs, model=model)
                print_verbose(f"response: {response}")
                if response != None:
                    return response

            except Exception as e:
                print_verbose(e)
                rate_limited_models.add(model)
                model_expiration_times[model] = (
                    time.time() + 60
                )  # cool down this selected model
                pass
    return response


def process_system_message(system_message, max_tokens, model):
    system_message_event = {"role": "system", "content": system_message}
    system_message_tokens = get_token_count(system_message_event, model)

    if system_message_tokens > max_tokens:
        print_verbose(
            "`tokentrimmer`: Warning, system message exceeds token limit. Trimming...")
        # shorten system message to fit within max_tokens
        new_system_message = shorten_message_to_fit_limit(
            system_message_event, max_tokens, model)
        system_message_tokens = get_token_count(new_system_message, model)

    return system_message_event, max_tokens - system_message_tokens


def process_messages(messages, max_tokens, model):
    # Process messages from older to more recent
    messages = messages[::-1]
    final_messages = []

    for message in messages:
        final_messages = attempt_message_addition(
            final_messages, message, max_tokens, model)

    return final_messages


def attempt_message_addition(final_messages, message, max_tokens, model):
    temp_messages = [message] + final_messages
    temp_message_tokens = get_token_count(messages=temp_messages, model=model)

    if temp_message_tokens <= max_tokens:
        return temp_messages

    # if temp_message_tokens > max_tokens, try shortening temp_messages
    elif "function_call" not in message:
        # fit updated_message to be within temp_message_tokens - max_tokens (aka the amount temp_message_tokens is greate than max_tokens)
        updated_message = shorten_message_to_fit_limit(
            message, temp_message_tokens - max_tokens, model)
        if can_add_message(updated_message, final_messages, max_tokens, model):
            return [updated_message] + final_messages

    return final_messages


def can_add_message(message, messages, max_tokens, model):
    if get_token_count(messages + [message], model) <= max_tokens:
        return True
    return False


def get_token_count(messages, model):
    return token_counter(model=model, messages=messages)


def shorten_message_to_fit_limit(
        message,
        tokens_needed,
        model):
    """
    Shorten a message to fit within a token limit by removing characters from the middle.
    """
    content = message["content"]

    while True:
        total_tokens = get_token_count([message], model)

        if total_tokens <= tokens_needed:
            break

        ratio = (tokens_needed) / total_tokens

        new_length = int(len(content) * ratio) - 1
        new_length = max(0, new_length)

        half_length = new_length // 2
        left_half = content[:half_length]
        right_half = content[-half_length:]

        trimmed_content = left_half + '..' + right_half
        message["content"] = trimmed_content
        content = trimmed_content

    return message

# LiteLLM token trimmer
# this code is borrowed from https://github.com/KillianLucas/tokentrim/blob/main/tokentrim/tokentrim.py
# Credits for this code go to Killian Lucas


def trim_messages(
    messages,
    model: Optional[str] = None,
    trim_ratio: float = 0.75,
    return_response_tokens: bool = False,
    max_tokens=None
):
    """
    Trim a list of messages to fit within a model's token limit.

    Args:
        messages: Input messages to be trimmed. Each message is a dictionary with 'role' and 'content'.
        model: The LiteLLM model being used (determines the token limit).
        trim_ratio: Target ratio of tokens to use after trimming. Default is 0.75, meaning it will trim messages so they use about 75% of the model's token limit.
        return_response_tokens: If True, also return the number of tokens left available for the response after trimming.
        max_tokens: Instead of specifying a model or trim_ratio, you can specify this directly.

    Returns:
        Trimmed messages and optionally the number of tokens available for response.
    """
    # Initialize max_tokens
    # if users pass in max tokens, trim to this amount
    try:
        print_verbose(f"trimming messages")
        if max_tokens == None:
            # Check if model is valid
            if model in litellm.model_cost:
                max_tokens_for_model = litellm.model_cost[model]['max_tokens']
                max_tokens = int(max_tokens_for_model * trim_ratio)
            else:
                # if user did not specify max tokens
                # or passed an llm litellm does not know
                # do nothing, just return messages
                return

        system_message = ""
        for message in messages:
            if message["role"] == "system":
                system_message += message["content"]

        current_tokens = token_counter(model=model, messages=messages)
        print_verbose(
            f"Current tokens: {current_tokens}, max tokens: {max_tokens}")

        # Do nothing if current tokens under messages
        if current_tokens < max_tokens:
            return messages

        # Trimming messages if current_tokens > max_tokens
        print_verbose(
            f"Need to trim input messages: {messages}, current_tokens{current_tokens}, max_tokens: {max_tokens}")
        if system_message:
            system_message_event, max_tokens = process_system_message(
                system_message=system_message, max_tokens=max_tokens, model=model)
            messages = messages + [system_message_event]

        final_messages = process_messages(
            messages=messages, max_tokens=max_tokens, model=model)

        if return_response_tokens:  # if user wants token count with new trimmed messages
            response_tokens = max_tokens - \
                get_token_count(final_messages, model)
            return final_messages, response_tokens

        return final_messages
    # [NON-Blocking, if error occurs just return final_messages
    except Exception as e:
        print_verbose(f"Got exception while token trimming{e}")
        return messages
