import json
import os
from typing import Any, Dict

import requests
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate

from config import DEFAULT_OLLAMA_API_PATH, DEFAULT_OLLAMA_BASE_URL, OLLAMA_MODEL, REWRITE_MODES
from services.schemas import CanonicalizationResult


PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    (
        "system",
        (
            "You are an expert in literature, culture, and semantic preservation. "
            "Rewrite user text according to the requested mode while preserving meaning. "
            "Return valid JSON only with keys: canonicalized_text, changed_phrases, "
            "preserved_concepts, nuance_risks, explanation. "
            "Use arrays of short strings for the list fields."
        ),
    ),
    (
        "user",
        (
            "Rewrite mode: {mode_name}\n"
            "Mode instruction: {mode_instruction}\n\n"
            "Analyze and rewrite the following text into canonical English.\n\n"
            "Text: {text}"
        ),
    ),
])


def _get_ollama_base_url() -> str:
    if "OLLAMA_BASE_URL" in st.secrets:
        return str(st.secrets["OLLAMA_BASE_URL"]).strip()
    return os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL).strip()


def _get_ollama_api_key() -> str | None:
    if "OLLAMA_API_KEY" in st.secrets:
        secret_value = str(st.secrets["OLLAMA_API_KEY"]).strip()
        return secret_value or None

    env_value = os.getenv("OLLAMA_API_KEY", "").strip()
    return env_value or None


def _get_generate_endpoint() -> str:
    base_url = _get_ollama_base_url().rstrip("/")
    if base_url.endswith("/api"):
        return f"{base_url}/generate"
    return f"{base_url}{DEFAULT_OLLAMA_API_PATH}"


def _generate_with_ollama(prompt: str) -> str:
    headers = {"Content-Type": "application/json"}
    api_key = _get_ollama_api_key()
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    response = requests.post(
        _get_generate_endpoint(),
        headers=headers,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    payload = response.json()
    return str(payload.get("response", "")).strip()


def _default_payload(text: str, raw_output: str) -> Dict[str, Any]:
    return {
        "canonicalized_text": raw_output.strip() or text,
        "changed_phrases": [],
        "preserved_concepts": [],
        "nuance_risks": ["Structured response could not be parsed reliably."],
        "explanation": "Fallback parsing was used because the model did not return valid JSON.",
    }


def _coerce_list(value: Any):
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def canonicalize_text(text: str, mode: str = "Simple") -> CanonicalizationResult:
    mode_instruction = REWRITE_MODES.get(mode, REWRITE_MODES["Simple"])
    formatted_prompt = PROMPT_TEMPLATE.format_messages(
        {
            "text": text,
            "mode_name": mode,
            "mode_instruction": mode_instruction,
        }
    )
    prompt = "\n\n".join(message.content for message in formatted_prompt)
    raw_output = _generate_with_ollama(prompt)

    try:
        payload = json.loads(raw_output)
    except json.JSONDecodeError:
        payload = _default_payload(text, raw_output)

    canonicalized_text = str(payload.get("canonicalized_text", "")).strip() or text
    changed_phrases = _coerce_list(payload.get("changed_phrases"))
    preserved_concepts = _coerce_list(payload.get("preserved_concepts"))
    nuance_risks = _coerce_list(payload.get("nuance_risks"))
    explanation = str(payload.get("explanation", "")).strip() or "No explanation was returned."

    return CanonicalizationResult(
        mode=mode,
        canonicalized_text=canonicalized_text,
        changed_phrases=changed_phrases,
        preserved_concepts=preserved_concepts,
        nuance_risks=nuance_risks,
        explanation=explanation,
    )
