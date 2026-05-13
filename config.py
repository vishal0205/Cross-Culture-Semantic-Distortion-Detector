OLLAMA_MODEL = "gpt-oss:120b-cloud"
DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_API_PATH = "/api/generate"
EMBEDDING_MODEL = "all-mpnet-base-v2"
HISTORY_DB_PATH = "analysis_history.db"

SIMILARITY_HIGH_THRESHOLD = 0.9
SIMILARITY_MEDIUM_THRESHOLD = 0.75
ENTITY_HIGH_THRESHOLD = 0.85
ENTITY_MEDIUM_THRESHOLD = 0.6
TOKEN_HIGH_THRESHOLD = 0.8
TOKEN_MEDIUM_THRESHOLD = 0.6

DEFAULT_TEXT = (
    "Despite the festival's joyful atmosphere, some visitors misunderstood "
    "the ritual symbolism and interpreted it as superstition."
)

REWRITE_MODES = {
    "Simple": "Rewrite into simple, direct English with minimal ambiguity.",
    "Literal": "Preserve the original meaning and details as literally as possible while improving clarity.",
    "Culturally Neutral": "Rewrite into neutral English that preserves meaning while reducing culture-specific assumptions.",
}
