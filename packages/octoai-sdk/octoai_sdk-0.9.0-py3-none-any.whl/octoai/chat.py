"""
Entities and APIs for working with text generation models.

Instead of using these classes directly, developers should
use the octoai.client.Client class. For example:

client = octoai.client.Client()
completion = client.chat.completions.create(...)
"""

from enum import Enum
from typing import Iterable, List, Optional, Union

from pydantic.v1 import BaseModel
from pydantic.v1.error_wrappers import ValidationError
from typing_extensions import Literal

from clients.ollm.models.chat_message import ChatMessage
from clients.ollm.models.create_chat_completion_request import (
    CreateChatCompletionRequest,
)
from clients.ollm.models.stop import Stop
from octoai.client import Client
from octoai.errors import OctoAIValidationError


class TextModel(str, Enum):
    """List of available text models."""

    LLAMA_2_13B_CHAT_FP16 = "llama-2-13b-chat-fp16"
    LLAMA_2_70B_CHAT_FP16 = "llama-2-70b-chat-fp16"
    CODELLAMA_7B_INSTRUCT_FP16 = "codellama-7b-instruct-fp16"
    CODELLAMA_13B_INSTRUCT_FP16 = "codellama-13b-instruct-fp16"
    CODELLAMA_34B_INSTRUCT_FP16 = "codellama-34b-instruct-fp16"
    CODELLAMA_70B_INSTRUCT_FP16 = "codellama-70b-instruct-fp16"
    MISTRAL_7B_INSTRUCT_FP16 = "mistral-7b-instruct-fp16"
    MIXTRAL_8X7B_INSTRUCT_FP16 = "mixtral-8x7b-instruct-fp16"

    def to_name(self):
        """Return the name of the model."""
        if self == self.LLAMA_2_13B_CHAT_FP16:
            return "llama-2-13b-chat-fp16"
        elif self == self.LLAMA_2_70B_CHAT_FP16:
            return "llama-2-70b-chat-fp16"
        elif self == self.CODELLAMA_7B_INSTRUCT_FP16:
            return "codellama-7b-instruct-fp16"
        elif self == self.CODELLAMA_13B_INSTRUCT_FP16:
            return "codellama-13b-instruct-fp16"
        elif self == self.CODELLAMA_34B_INSTRUCT_FP16:
            return "codellama-34b-instruct-fp16"
        elif self == self.CODELLAMA_70B_INSTRUCT_FP16:
            return "codellama-70b-instruct-fp16"
        elif self == self.MISTRAL_7B_INSTRUCT_FP16:
            return "mistral-7b-instruct-fp16"
        elif self == self.MIXTRAL_8X7B_INSTRUCT_FP16:
            return "mixtral-8x7b-instruct-fp16"


def get_model_list() -> List[str]:
    """Return a list of available text models."""
    return [model.value for model in TextModel]


class ChoiceDelta(BaseModel):
    """Contents for streaming text completion responses."""

    content: Optional[str] = None
    role: Optional[Literal["system", "user", "assistant", "tool"]] = None


class Choice(BaseModel):
    """A single choice in a text completion response."""

    index: int
    message: ChatMessage = None
    delta: ChoiceDelta = None
    finish_reason: Literal[
        "stop", "length", "tool_calls", "content_filter", "function_call"
    ] = None


class CompletionUsage(BaseModel):
    """Usage statistics for a text completion response."""

    completion_tokens: int
    prompt_tokens: int
    total_tokens: int


class ChatCompletion(BaseModel):
    """A text completion response."""

    id: str
    choices: List[Choice]
    created: int
    model: str
    object: Optional[Literal["chat.completion", "chat.completion.chunk"]] = None
    system_fingerprint: Optional[str] = None
    usage: Optional[CompletionUsage] = None


class Completions:
    """Text completions API."""

    client: Client
    endpoint: str = "https://text.octoai.run/v1/chat/completions"

    def __init__(self, client: Client) -> None:
        self.client = client

    def create(
        self,
        *,
        messages: List[ChatMessage],
        model: Union[str, TextModel],
        frequency_penalty: Optional[float] = None,
        max_tokens: Optional[int] = None,
        presence_penalty: Optional[float] = 0.0,
        stop: Optional[Union[Stop, List[str]]] = None,
        stream: Optional[bool] = False,
        temperature: Optional[float] = 1.0,
        top_p: Optional[float] = 1.0,
    ) -> Union[ChatCompletion, Iterable[ChatCompletion]]:
        """
        Create a chat completion with a text generation model.

        :param messages: Required. A list of messages to use as context for the
            completion.
        :param model: Required. The model to use for the completion. Supported models
            are listed in the `octoai.chat.TextModel` enum.
        :param frequency_penalty: Positive values make it less likely that the model
            repeats tokens several times in the completion. Valid values are between
            -2.0 and 2.0.
        :param max_tokens: The maximum number of tokens to generate.
        :param presence_penalty: Positive values make it less likely that the model
            repeats tokens in the completion. Valid values are between -2.0 and 2.0.
        :param stop: A list of sequences where the model stops generating tokens.
        :param stream: Whether to return a generator that yields partial message
            deltas as they become available, instead of waiting to return the entire
            response.
        :param temperature: Sampling temperature. A value between 0 and 2. Higher values
            make the model more creative by sampling less likely tokens.
        :param top_p: The cumulative probability of the most likely tokens to use. Use
            `temperature` or `top_p` but not both.
        """
        request = CreateChatCompletionRequest(
            messages=messages,
            model=model.value if isinstance(model, TextModel) else model,
            frequency_penalty=frequency_penalty,
            function_call=None,
            functions=None,
            logit_bias=None,
            max_tokens=max_tokens,
            n=1,
            presence_penalty=presence_penalty,
            stop=stop if isinstance(stop, Stop) else Stop(stop),
            stream=stream,
            temperature=temperature,
            top_p=top_p,
            user=None,
        )

        inputs = request.to_dict()

        if stream:
            return self.client.infer_stream(
                self.endpoint, inputs, map_fn=lambda resp: ChatCompletion(**resp)
            )  # type: ignore

        resp = self.client.infer(self.endpoint, inputs)
        try:
            return ChatCompletion(**resp)
        except ValidationError as e:
            raise OctoAIValidationError(
                "Unable to validate response from server.", caused_by=e
            )


class Chat:
    """Chat API for text generation models."""

    completions: Completions

    def __init__(self, client: Client):
        self.completions = Completions(client)
