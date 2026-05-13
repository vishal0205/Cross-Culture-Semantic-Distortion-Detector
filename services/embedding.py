import os

import streamlit as st
from huggingface_hub.utils import disable_progress_bars
from sentence_transformers import SentenceTransformer
from transformers.utils import logging as transformers_logging

from config import EMBEDDING_MODEL


os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TQDM_DISABLE"] = "1"


@st.cache_resource
def get_embedding_model():
    disable_progress_bars()
    transformers_logging.disable_progress_bar()
    return SentenceTransformer(EMBEDDING_MODEL)


def generate_embedding(text: str):
    return get_embedding_model().encode(text, show_progress_bar=False)
