"""Structured information from local or remote LLMs."""

__version__ = "0.2.2"

__all__ = [
    "ModelDir", "FormatDir"
    "Model", "TextModel", "MessagesModel", "Tokenizer",
    "GenConf", "GenRes", "GenError", "GenOut",
    "LlamaCppModel", "LlamaCppTokenizer",
    "OpenAIModel", "OpenAITokenizer",
    "Thread", "MsgKind",
    "Context", "Trim",
    "JSchemaConf",
]

__author__ = "Jorge Diogo"


from .gen import (
    GenConf,
    GenRes,
    GenError,
    GenOut
)

from .thread import (
    Thread,
    MsgKind,
)

from .model import (
    Model,
    TextModel,
    FormattedTextModel,
    MessagesModel,
    Tokenizer
)

from .llamacpp import (
    LlamaCppModel,
    LlamaCppTokenizer
)

from .openai import (
    OpenAIModel,
    OpenAITokenizer
)

from .context import (
    Context,
    Trim
)

from .modeldir import ModelDir

from .formatdir import FormatDir

from .json_utils import JSchemaConf
