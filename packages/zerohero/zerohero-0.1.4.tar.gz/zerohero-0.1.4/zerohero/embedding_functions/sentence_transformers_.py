"""Makes a embedding function from a sentence_transformers model."""
import numpy as np
import torch
from sentence_transformers import SentenceTransformer


def make_sentence_transformers_embedding_function(model_name: str):
    """Makes a embedding function from a sentence_transformers model.

    Args:
        model_name (str): Name of a pretrained Sentence Transformers model.

    Returns:
        Callable: A function that maps text to an embedding.
    """
    model = SentenceTransformer(
        model_name, device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
    )

    def sentence_transformers_embedding_function(text):
        return np.array(model.encode(text))

    return sentence_transformers_embedding_function
