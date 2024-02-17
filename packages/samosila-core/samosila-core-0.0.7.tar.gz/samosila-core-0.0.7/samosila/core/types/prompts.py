import json
import yaml
import warnings
from abc import ABC, abstractmethod
from string import Formatter
from typing import Any, Callable, Dict, List, Mapping, Optional, Union
from pathlib import Path
from pydantic import Field

from .response_types import BaseMessage, BaseModel, HumanMessage



def get_template_variables(template: str) -> List[str]:
    input_variables = {
            v for _, v, _, _ in Formatter().parse(template) if v is not None
        }
    
    return sorted(input_variables)



class PromptValue(BaseModel):
    """String prompt value."""

    text: str

    def to_string(self) -> str:
        """Return prompt as string."""
        return self.text

    def to_messages(self) -> List[BaseMessage]:
        """Return prompt as messages."""
        return [HumanMessage(content=self.text)]



class BasePromptTemplate(PromptValue, ABC):
    """Base class for all prompt templates, returning a prompt."""

    input_variables: List[str]
    input_types: Dict[str, Any] = Field(default_factory=dict)
    partial_variables: Mapping[str, Union[str, Callable[[], str]]] = Field(
        default_factory=dict
    )

    class Config:
        arbitrary_types_allowed = True

    def _format_prompt_with_error_handling(self, inner_input: Dict) -> PromptValue:
        try:
            input_dict = {key: inner_input[key] for key in self.input_variables}
        except TypeError as e:
            raise TypeError(
                f"Expected mapping type as input to {self.__class__.__name__}. "
                f"Received {type(inner_input)}."
            ) from e
        except KeyError as e:
            raise KeyError(
                f"Input to {self.__class__.__name__} is missing variable {e}. "
                f" Expected: {self.input_variables}"
                f" Received: {list(inner_input.keys())}"
            ) from e
        return self.format_prompt(**input_dict)


    @abstractmethod
    def format_prompt(self, **kwargs: Any) -> PromptValue:
        """Create Chat Messages."""


    def partial(self, **kwargs: Union[str, Callable[[], str]]) -> "BasePromptTemplate":
        """Return a partial of the prompt template."""
        prompt_dict = self.__dict__.copy()
        prompt_dict["input_variables"] = list(
            set(self.input_variables).difference(kwargs)
        )
        prompt_dict["partial_variables"] = {**self.partial_variables, **kwargs}
        return type(self)(**prompt_dict)

    def _merge_partial_and_user_variables(self, **kwargs: Any) -> Dict[str, Any]:
        # Get partial params:
        partial_kwargs = {
            k: v if isinstance(v, str) else v()
            for k, v in self.partial_variables.items()
        }
        return {**partial_kwargs, **kwargs}

    @abstractmethod
    def format(self, **kwargs: Any) -> str:
        """Format the prompt with the inputs.

        Args:
            kwargs: Any arguments to be passed to the prompt template.

        Returns:
            A formatted string.

        Example:

        .. code-block:: python

            prompt.format(variable1="foo")
        """

    @property
    def _prompt_type(self) -> str:
        """Return the prompt type key."""
        raise NotImplementedError

    def dict(self, **kwargs: Any) -> Dict:
        """Return dictionary representation of prompt."""
        prompt_dict = super().dict(**kwargs)
        try:
            prompt_dict["_type"] = self._prompt_type
        except NotImplementedError:
            pass
        return prompt_dict

    def save(self, file_path: Union[Path, str]) -> None:
        """Save the prompt.

        Args:
            file_path: Path to directory to save prompt to.

        Example:
        .. code-block:: python

            prompt.save(file_path="path/prompt.yaml")
        """
        if self.partial_variables:
            raise ValueError("Cannot save prompt with partial variables.")

        # Fetch dictionary to save
        prompt_dict = self.dict()
        if "_type" not in prompt_dict:
            raise NotImplementedError(f"Prompt {self} does not support saving.")

        # Convert file to Path object.
        if isinstance(file_path, str):
            save_path = Path(file_path)
        else:
            save_path = file_path

        directory_path = save_path.parent
        directory_path.mkdir(parents=True, exist_ok=True)

        if save_path.suffix == ".json":
            with open(file_path, "w") as f:
                json.dump(prompt_dict, f, indent=4)
        elif save_path.suffix == ".yaml":
            with open(file_path, "w") as f:
                yaml.dump(prompt_dict, f, default_flow_style=False)
        else:
            raise ValueError(f"{save_path} must be json or yaml")


class StringPromptTemplate(BasePromptTemplate, ABC):
    """String prompt that exposes the format method, returning a prompt."""


    def format_prompt(self, **kwargs: Any) -> PromptValue:
        """Create Chat Messages."""
        return PromptValue(text=self.format(**kwargs))



class PromptTemplate(StringPromptTemplate):
    """A prompt template for a language model.

    Example:

        .. code-block:: python

            from samosila.core import PromptTemplate

            # Instantiation using from_template (recommended)
            prompt = PromptTemplate.from_template("Say {foo}")
            prompt.format(foo="bar")

            # Instantiation using initializer
            prompt = PromptTemplate(input_variables=["foo"], template="Say {foo}")
    """

    input_variables: List[str]
    """A list of the names of the variables the prompt template expects."""

    template: str
    """The prompt template."""

    def __add__(self, other: Any) -> "PromptTemplate":
        """Override the + operator to allow for combining prompt templates."""
        # Allow for easy combining
        if isinstance(other, PromptTemplate):
            input_variables = list(
                set(self.input_variables) | set(other.input_variables)
            )
            template = self.template + other.template
            # If any do not want to validate, then don't
            partial_variables = {k: v for k, v in self.partial_variables.items()}
            for k, v in other.partial_variables.items():
                if k in partial_variables:
                    raise ValueError("Cannot have same variable partialed twice.")
                else:
                    partial_variables[k] = v
            return PromptTemplate(
                text=template,
                template=template,
                input_variables=input_variables,
                partial_variables=partial_variables,
            )
        elif isinstance(other, str):
            prompt = PromptTemplate.from_template(other)
            return self + prompt
        else:
            raise NotImplementedError(f"Unsupported operand type for +: {type(other)}")


    def format(self, **kwargs: Any) -> str:
        """Format the prompt with the inputs.

        Args:
            kwargs: Any arguments to be passed to the prompt template.

        Returns:
            A formatted string.

        Example:

            .. code-block:: python

                prompt.format(variable1="foo")
        """
        kwargs = self._merge_partial_and_user_variables(**kwargs)
        return Formatter().format(self.template, **kwargs)

    @classmethod
    def from_examples(
        cls,
        examples: List[str],
        suffix: str,
        input_variables: List[str],
        example_separator: str = "\n\n",
        prefix: str = "",
        **kwargs: Any,
    ) -> "PromptTemplate":
        """Take examples in list format with prefix and suffix to create a prompt.

        Intended to be used as a way to dynamically create a prompt from examples.

        Args:
            examples: List of examples to use in the prompt.
            suffix: String to go after the list of examples. Should generally
                set up the user's input.
            input_variables: A list of variable names the final prompt template
                will expect.
            example_separator: The separator to use in between examples. Defaults
                to two new line characters.
            prefix: String that should go before any examples. Generally includes
                examples. Default to an empty string.

        Returns:
            The final prompt generated.
        """
        template = example_separator.join([prefix, *examples, suffix])
        return cls(input_variables=input_variables, template=template, **kwargs)

    @classmethod
    def from_file(
        cls,
        template_file: Union[str, Path],
        input_variables: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> "PromptTemplate":
        """Load a prompt from a file.

        Args:
            template_file: The path to the file containing the prompt template.
            input_variables: [DEPRECATED] A list of variable names the final prompt
                template will expect.

        input_variables is ignored as from_file now delegates to from_template().

        Returns:
            The prompt loaded from the file.
        """
        with open(str(template_file), "r") as f:
            template = f.read()
        if input_variables:
            warnings.warn(
                "`input_variables' is deprecated and ignored.", DeprecationWarning
            )
        return cls.from_template(template=template, **kwargs)

    @classmethod
    def from_template(
        cls,
        template: str,
        *,
        partial_variables: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "PromptTemplate":
        """Load a prompt template from a template.

        Args:
            template: The template to load.
            partial_variables: A dictionary of variables that can be used to partially
                               fill in the template. For example, if the template is
                              `"{variable1} {variable2}"`, and `partial_variables` is
                              `{"variable1": "foo"}`, then the final prompt will be
                              `"foo {variable2}"`.

        Returns:
            The prompt template loaded from the template.
        """

        input_variables = get_template_variables(template)
        _partial_variables = partial_variables or {}

        if _partial_variables:
            input_variables = [
                var for var in input_variables if var not in _partial_variables
            ]

        return cls(
            input_variables=input_variables,
            template=template,
            partial_variables=_partial_variables,
            **kwargs,
        )



# class AIMessagePromptTemplate(StringPromptTemplate):


#     def format(self, **kwargs: Any) -> BaseMessage:
#         """Format the prompt template.

#         Args:
#             **kwargs: Keyword arguments to use for formatting.

#         Returns:
#             Formatted message.
#         """
#         text = self.prompt.format(**kwargs)
#         return AIMessage(content=text, additional_kwargs=self.additional_kwargs)
