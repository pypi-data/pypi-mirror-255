from copy import deepcopy
from typing import Any, Dict, Optional

from ...types import (
    FeaturesState, ChatData,
    CallbackHandler, CompletionData
)


def import_aim() -> Any:
    """Import the aim python package and raise an error if it is not installed."""
    try:
        import aim
    except ImportError:
        raise ImportError(
            "To use the Aim callback manager you need to have the"
            " `aim` python package installed."
            "Please install it with `pip install aim`"
        )
    return aim


class BaseMetadataCallbackHandler:
    """This class handles the metadata and associated function states for callbacks.

    Attributes:
        step (int): The current step.
        starts (int): The number of times the start method has been called.
        ends (int): The number of times the end method has been called.
        errors (int): The number of times the error method has been called.
        text_ctr (int): The number of times the text method has been called.
        always_verbose_ (bool): Whether to always be verbose.
    """

    def __init__(self) -> None:
        self.step = 0
        self.llm_starts = 0
        self.llm_ends = 0
        self.starts = 0
        self.ends = 0
        self.errors = 0
        self.text_ctr = 0

    def get_custom_callback_meta(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "starts": self.starts,
            "ends": self.ends,
            "llm_starts": self.llm_starts,
            "llm_ends": self.llm_ends,
            "errors": self.errors,
            "text_ctr": self.text_ctr,
        }

    def reset_callback_meta(self) -> None:
        """Reset the callback metadata."""
        self.step = 0
        self.starts = 0
        self.ends = 0
        self.llm_starts = 0
        self.llm_ends = 0
        self.errors = 0
        self.text_ctr = 0

        return None


class AimCallbackHandler(CallbackHandler, BaseMetadataCallbackHandler):
    """Callback Handler that logs to Aim.

    Parameters:
        repo (:obj:`str`, optional): Aim repository path or Repo object to which
            Run object is bound. If skipped, default Repo is used.
        experiment_name (:obj:`str`, optional): Sets Run's `experiment` property.
            'default' if not specified. Can be used later to query runs/sequences.
        system_tracking_interval (:obj:`int`, optional): Sets the tracking interval
            in seconds for system usage metrics (CPU, Memory, etc.). Set to `None`
             to disable system metrics tracking.
        log_system_params (:obj:`bool`, optional): Enable/Disable logging of system
            params such as installed packages, git info, environment variables, etc.

    This handler will utilize the associated callback method called and formats
    the input of each callback function with metadata regarding the state of LLM run
    and then logs the response to Aim.
    """

    def __init__(
        self,
        repo: Optional[str] = None,
        experiment_name: Optional[str] = None,
        system_tracking_interval: Optional[int] = 10,
        log_system_params: bool = True,
        features_state: Optional[FeaturesState] = None,
    ) -> None:
        """Initialize callback handler."""

        if features_state is None:
            features_state = FeaturesState.only(
                {"on_llm_end": True, "on_chat_end": True,
                    "on_llm_start": True, "on_chat_start": True}
            )
        super().__init__(features_state)

        aim = import_aim()
        self.repo = repo
        self.experiment_name = experiment_name
        self.system_tracking_interval = system_tracking_interval
        self.log_system_params = log_system_params
        self._run = aim.Run(
            repo=self.repo,
            experiment=self.experiment_name,
            system_tracking_interval=self.system_tracking_interval,
            log_system_params=self.log_system_params,
        )
        self._run_hash = self._run.hash
        self.action_records: list = []

    def setup(self, **kwargs: Any) -> None:
        aim = import_aim()

        if not self._run:
            if self._run_hash:
                self._run = aim.Run(
                    self._run_hash,
                    repo=self.repo,
                    system_tracking_interval=self.system_tracking_interval,
                )
            else:
                self._run = aim.Run(
                    repo=self.repo,
                    experiment=self.experiment_name,
                    system_tracking_interval=self.system_tracking_interval,
                    log_system_params=self.log_system_params,
                )
                self._run_hash = self._run.hash

        if kwargs:
            for key, value in kwargs.items():
                self._run.set(key, value, strict=False)

    def on_llm_start(
        self, data: CompletionData, **kwargs
    ) -> None:
        """Run when LLM starts."""
        aim = import_aim()

        self.step += 1
        self.llm_starts += 1
        self.starts += 1

        resp = {"action": "on_llm_start"}
        resp.update(self.get_custom_callback_meta())

        prompts_res = deepcopy(data.prompt)

        self._run.track(
            [aim.Text(prompts_res.content)],
            name="on_llm_start",
            context=resp,
        )

    def on_llm_end(self, data: CompletionData, **kwargs) -> None:
        """Run when LLM ends running."""
        aim = import_aim()
        self.step += 1
        self.llm_ends += 1
        self.ends += 1

        resp = {"action": "on_llm_end"}
        resp.update(self.get_custom_callback_meta())

        response_res = deepcopy(data.response)

        generated = [
            aim.Text(res.text)
            for res in (response_res or [])
        ]
        self._run.track(
            generated,
            name="on_llm_end",
            context=resp,
        )

    def on_chat_start(
        self, data: ChatData, **kwargs
    ) -> None:
        """Run when LLM starts."""
        aim = import_aim()

        self.step += 1
        self.llm_starts += 1
        self.starts += 1

        resp = {"action": "on_chat_start"}
        resp.update(self.get_custom_callback_meta())

        prompts_res = deepcopy(data.messages)

        self._run.track(
            [aim.Text(message.content) for message in prompts_res],
            name="on_chat_start",
            context=resp,
        )

    def on_chat_end(self, data: ChatData, **kwargs) -> None:
        """Run when LLM ends running."""
        aim = import_aim()
        self.step += 1
        self.llm_ends += 1
        self.ends += 1

        resp = {"action": "on_chat_end"}
        resp.update(self.get_custom_callback_meta())

        response_res = deepcopy(data.response)

        generated = [
            aim.Text(res.message.content)
            for res in (response_res or [])
        ]
        self._run.track(
            generated,
            name="on_chat_end",
            context=resp,
        )

    # def on_tool_start(
    #     self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    # ) -> None:
    #     """Run when tool starts running."""
    #     aim = import_aim()
    #     self.step += 1
    #     self.tool_starts += 1
    #     self.starts += 1

    #     resp = {"action": "on_tool_start"}
    #     resp.update(self.get_custom_callback_meta())

    #     self._run.track(aim.Text(input_str),
    #                     name="on_tool_start", context=resp)

    # def on_tool_end(self, output: str, **kwargs: Any) -> None:
    #     """Run when tool ends running."""
    #     aim = import_aim()
    #     self.step += 1
    #     self.tool_ends += 1
    #     self.ends += 1

    #     resp = {"action": "on_tool_end"}
    #     resp.update(self.get_custom_callback_meta())

    #     self._run.track(aim.Text(output), name="on_tool_end", context=resp)

    # def on_tool_error(self, error: BaseException, **kwargs: Any) -> None:
    #     """Run when tool errors."""
    #     self.step += 1
    #     self.errors += 1

    def flush_tracker(
        self,
        repo: Optional[str] = None,
        experiment_name: Optional[str] = None,
        system_tracking_interval: Optional[int] = 10,
        log_system_params: bool = True,
        langchain_asset: Any = None,
        reset: bool = True,
        finish: bool = False,
    ) -> None:
        """Flush the tracker and reset the session.

        Args:
            repo (:obj:`str`, optional): Aim repository path or Repo object to which
                Run object is bound. If skipped, default Repo is used.
            experiment_name (:obj:`str`, optional): Sets Run's `experiment` property.
                'default' if not specified. Can be used later to query runs/sequences.
            system_tracking_interval (:obj:`int`, optional): Sets the tracking interval
                in seconds for system usage metrics (CPU, Memory, etc.). Set to `None`
                 to disable system metrics tracking.
            log_system_params (:obj:`bool`, optional): Enable/Disable logging of system
                params such as installed packages, git info, environment variables, etc.
            langchain_asset: The langchain asset to save.
            reset: Whether to reset the session.
            finish: Whether to finish the run.

            Returns:
                None
        """

        if langchain_asset:
            try:
                for key, value in langchain_asset.dict().items():
                    self._run.set(key, value, strict=False)
            except Exception:
                pass

        if finish or reset:
            self._run.close()
            self.reset_callback_meta()
        if reset:
            self.__init__(  # type: ignore
                repo=repo if repo else self.repo,
                experiment_name=experiment_name
                if experiment_name
                else self.experiment_name,
                system_tracking_interval=system_tracking_interval
                if system_tracking_interval
                else self.system_tracking_interval,
                log_system_params=log_system_params
                if log_system_params
                else self.log_system_params,
            )
