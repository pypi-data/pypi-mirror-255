"""Makes a embedding function from a openai model."""

import backoff
import tiktoken
import openai
import numpy as np

OPENAI_MODEL_NAME_TO_MAX_TOKENS = {"text-embedding-ada-002": 8191}


def _backoff_hdlr(details):
    """A callback for backoff to report status.

    Args:
        details (dict): Details form backoff.
    """
    # pylint: disable=consider-using-f-string
    print(
        "Backing off {wait:0.1f} seconds after {tries} tries "
        "\n {exception}".format(**details)
    )


def _openai_lookup_max_tokens(model_name: str) -> int:
    """Looks up the max tokens for an openai embedding model.

    Args:
        model_name (str): Name of an OpenAI model.

    Returns:
        int: the maximum number of tokens the model can accommodate.
    """
    return OPENAI_MODEL_NAME_TO_MAX_TOKENS.get(model_name, 2046)


def make_openai_embedding_function(model_name, openai_api_key):
    """Makes a embedding function from an OpenAI model.

    Args:
        model_name (str): Name of an OpenAI model.
        openai_api_key (str): An OpenAI API key.

    Returns:
        Callable: A function that maps text to an embedding.
    """
    openai.api_key = openai_api_key

    max_tokens = _openai_lookup_max_tokens(model_name=model_name)

    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    # do a dry run to see if embeddings are supported by the passed model
    try:
        openai.Embedding.create(input="test", model=model_name)["data"][0]["embedding"]
    except Exception as exc:
        raise ValueError(
            f"The mode {model_name=} does not support embeddings."
        ) from exc

    # openai can make ai, but can they make api? no.
    @backoff.on_exception(
        backoff.constant, openai.error.RateLimitError, on_backoff=_backoff_hdlr
    )
    @backoff.on_exception(
        backoff.constant, openai.error.APIConnectionError, on_backoff=_backoff_hdlr
    )
    @backoff.on_exception(backoff.expo, openai.error.Timeout, on_backoff=_backoff_hdlr)
    @backoff.on_exception(backoff.expo, openai.error.APIError, on_backoff=_backoff_hdlr)
    def _openai_embedding_function(text):
        truncated_text = encoding.decode(encoding.encode(text)[:max_tokens])

        return np.array(
            openai.Embedding.create(input=truncated_text, model=model_name)["data"][0][
                "embedding"
            ]
        )

    return _openai_embedding_function
