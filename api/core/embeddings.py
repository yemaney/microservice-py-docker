"""This module is concerned with generating and managing vector embeddings for file content using OpenRouter API."""

import os

import anyio
import httpx


def get_openrouter_api_key() -> str:
    """
    Get the OpenRouter API key from environment variables.

    Returns
    -------
    str
        The OpenRouter API key.

    Raises
    ------
    ValueError
        If the API key is not found in environment variables.

    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        msg = "OPENROUTER_API_KEY environment variable is not set"
        raise ValueError(msg)
    return api_key


async def generate_embedding(text: str) -> list[float]:
    """
    Generate vector embedding for text content using OpenRouter API.

    Parameters
    ----------
    text : str
        The text content to embed.

    Returns
    -------
    List[float]
        The vector embedding as a list of floats.

    Raises
    ------
    httpx.HTTPError
        If the API request fails.
    ValueError
        If the API response is invalid.

    """
    api_key = get_openrouter_api_key()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/embeddings",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "qwen/qwen3-embedding-8b",
                "input": text,
            },
            timeout=30.0,
        )

        response.raise_for_status()
        data = response.json()

        # Extract embedding from response
        # OpenRouter API typically returns: {"data": [{"embedding": [...], ...}], "usage": {...}}
        if "data" not in data or not data["data"]:
            msg = "Invalid response from OpenRouter API"
            raise ValueError(msg)

        return data["data"][0]["embedding"]


async def generate_embedding_from_file(file_path: str) -> list[float]:
    """
    Generate vector embedding from file content using OpenRouter API.

    Parameters
    ----------
    file_path : str
        Path to the file to read and embed.

    Returns
    -------
    List[float]
        The vector embedding as a list of floats.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    UnicodeDecodeError
        If the file cannot be decoded as UTF-8 text.
    httpx.HTTPError
        If the API request fails.

    """

    content = await anyio.Path(file_path).read_text(encoding="utf-8")

    # For text files, we can embed the entire content
    # For very large files, you might want to chunk them
    return await generate_embedding(content)
