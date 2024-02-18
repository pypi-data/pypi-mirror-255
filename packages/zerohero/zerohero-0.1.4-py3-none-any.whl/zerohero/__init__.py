"""Interface and functions that are generic across backends.
`make_zero_shot_classifier` is currently the only public function.
"""

from collections import OrderedDict
from collections.abc import Callable
from typing import Literal

import numpy as np
import openai
import torch
from sentence_transformers import util

from zerohero.embedding_functions.openai_ import make_openai_embedding_function
from zerohero.embedding_functions.sentence_transformers_ import (
    make_sentence_transformers_embedding_function,
)

MODEL_TYPES = {"openai", "sentence-transformers"}


def make_zero_shot_classifier(
    categories: list,
    model_type: Literal["sentence-transformers", "openai"],
    model_name: str,
    openai_api_key: str = None,
) -> Callable[[str], dict]:
    """Given as list of possible categories,
    returns a function that takes a string of text to be classified
    and returns a dictionary of classification results
    created by a zero-shot classifier based on embedding created
    by the specified model.

    The function's output dict's keys and values are:

    category (str): the predicted category
        (selected from the categories according to cosine similarity of the embeddings).
    probability (float): the probability (between 0 and 1) of the selected category
        (according to "distribution").
    similarities (dict): A dictionary containing the similarities.
        The keys are the categories,
        the values are the cosine similarities (between -1 and 1)
        between the text's embedding and the categories embedding.
    distribution (dict): A dictionary containing the probability distribution.
        The keys are the categories,
        the value is the probability (between 0 and 1)
        calculated by applying softmax to the "similarities".

    Args:
        categories (list): A list of possible categories.
            For best results, categories should be straightforward and meaningful.
        model_type (str): One of "openai" or "sentence-transformers".
        model_name (str): An embedding model that matches the model_type.
            For a list of supported embedding models for model_type="openai" see:
            https://platform.openai.com/docs/models/embeddings
            For a list of supported embedding models for model_type="sentence-transformers" see:
            https://www.sbert.net/docs/pretrained_models.html#model-overview
        openai_api_key (str, optional): When model_type="openai", must pass an OpenAI API key.
            Defaults to None.

    Returns:
        Callable[[str], dict]: The embedding based zero-shot classifier.
    """
    if not model_type in MODEL_TYPES:
        raise ValueError(
            f"{model_type=} not valid, must be one of {', '.join(MODEL_TYPES)}"
        )

    if model_type == "sentence-transformers":
        embedding_function = make_sentence_transformers_embedding_function(
            model_name=model_name
        )
    if model_type == "openai":
        if not openai_api_key:
            raise ValueError(
                "When using model_type=openai, openai_api_key must be passed."
            )

        openai.api_key = openai_api_key
        model_names = [model["id"] for model in openai.Model.list()["data"]]

        if not model_name in model_names:
            raise ValueError(
                f"{model_name=} not valid, must be one of {', '.join(model_names)}"
            )

        embedding_function = make_openai_embedding_function(
            model_name=model_name, openai_api_key=openai_api_key
        )

    return _make_zero_shot_embedding_classifier(
        categories=categories, embedding_function=embedding_function
    )


def _make_zero_shot_embedding_classifier(categories, embedding_function):
    categories_encoded = torch.tensor(
        np.array([embedding_function(category) for category in categories])
    )

    def embedding_classifier(text):
        text_encoded = torch.tensor(embedding_function(text))
        similarities = util.cos_sim(text_encoded, categories_encoded).flatten()

        category_similarities = dict(
            zip(categories, [float(similarity) for similarity in similarities])
        )

        softmax_similarities = [
            float(sf_sim)
            for sf_sim in torch.nn.functional.softmax(similarities, dim=-1)
        ]

        distribution_sorted = OrderedDict(
            sorted(
                zip(categories, softmax_similarities),
                key=lambda t: t[1],
                reverse=True,
            )
        )

        category = list(distribution_sorted.keys())[0]
        category_confidence = list(distribution_sorted.values())[0]

        return {
            "category": category,
            "probability": category_confidence,
            "distribution": dict(distribution_sorted),
            "similarities": category_similarities,
        }

    return embedding_classifier
