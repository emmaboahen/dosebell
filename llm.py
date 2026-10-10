import logging

from anthropic import Anthropic
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

model = "claude-haiku-5-5"
max_tokens = 1000

_client = None


def get_client() -> Anthropic:
    global _client
    if _client is None:
        load_dotenv()
        _client = Anthropic()
    return _client


def chat(messages, system=None, stop_sequences=None, tools=None):
    params = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
        "stop_sequences": stop_sequences or [],
    }

    if tools:
        params["tools"] = tools

    if system:
        params["system"] = system

    try:
        return get_client().messages.create(**params)
    except Exception:
        logger.exception("Failed to create message")
        raise
