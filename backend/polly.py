"""Amazon Polly TTS client for voice synthesis.

NOTE: Polly requires standard AWS credentials (access key + secret key).
The Bedrock-specific bearer token does not work with Polly.
Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables,
or configure credentials via ~/.aws/credentials.
"""

import asyncio
import logging
import re
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from typing import Optional, List
from .config import AWS_REGION

logger = logging.getLogger("llm_council.polly")

# Polly has a 3000 character limit for synthesize_speech
POLLY_MAX_CHARS = 2900  # Leave some margin


def _get_polly_client():
    """Create a Polly client."""
    return boto3.client(
        'polly',
        region_name=AWS_REGION
    )


def _split_text_into_chunks(text: str, max_chars: int = POLLY_MAX_CHARS) -> List[str]:
    """
    Split text into chunks that fit within Polly's character limit.
    Tries to split at sentence boundaries.

    Args:
        text: Text to split
        max_chars: Maximum characters per chunk

    Returns:
        List of text chunks
    """
    if len(text) <= max_chars:
        return [text]

    chunks = []
    remaining = text

    while remaining:
        if len(remaining) <= max_chars:
            chunks.append(remaining)
            break

        # Find a good split point (sentence end)
        chunk = remaining[:max_chars]

        # Try to split at sentence boundary
        split_patterns = [
            r'\.\s+',  # Period followed by space
            r'\?\s+',  # Question mark followed by space
            r'!\s+',   # Exclamation mark followed by space
            r'\n\n',   # Paragraph break
            r'\n',     # Line break
            r',\s+',   # Comma followed by space
            r':\s+',   # Colon followed by space
        ]

        split_pos = None
        for pattern in split_patterns:
            matches = list(re.finditer(pattern, chunk))
            if matches:
                # Use the last match
                split_pos = matches[-1].end()
                break

        if split_pos and split_pos > max_chars // 2:
            # Found a good split point
            chunks.append(remaining[:split_pos].strip())
            remaining = remaining[split_pos:].strip()
        else:
            # No good split point, split at word boundary
            space_pos = chunk.rfind(' ')
            if space_pos > max_chars // 2:
                chunks.append(remaining[:space_pos].strip())
                remaining = remaining[space_pos:].strip()
            else:
                # Last resort: hard split
                chunks.append(chunk)
                remaining = remaining[max_chars:].strip()

    return chunks


def _synthesize_chunk(
    client,
    text: str,
    voice_id: str,
    output_format: str,
    engine: str = 'neural'
) -> Optional[bytes]:
    """Synthesize a single chunk of text."""
    try:
        response = client.synthesize_speech(
            Text=text,
            OutputFormat=output_format,
            VoiceId=voice_id,
            Engine=engine
        )
        audio_stream = response.get('AudioStream')
        if audio_stream:
            return audio_stream.read()
        return None
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code == 'InvalidParameterValue' and engine == 'neural':
            # Fallback to standard engine
            return _synthesize_chunk(client, text, voice_id, output_format, 'standard')
        raise


def _sync_synthesize_speech(
    client,
    text: str,
    voice_id: str = "Matthew",
    output_format: str = "mp3"
) -> Optional[bytes]:
    """
    Synchronous speech synthesis (runs in thread pool).
    Handles long text by splitting into chunks.

    Args:
        client: Boto3 Polly client
        text: Text to synthesize
        voice_id: Polly voice ID (e.g., "Matthew", "Joanna", "Amy")
        output_format: Audio format ("mp3", "ogg_vorbis", "pcm")

    Returns:
        Audio bytes or None if failed
    """
    try:
        # Split text into chunks if needed
        chunks = _split_text_into_chunks(text)
        logger.info(f"Synthesizing {len(chunks)} chunk(s) with voice {voice_id}")

        audio_parts = []
        for i, chunk in enumerate(chunks):
            logger.debug(f"Synthesizing chunk {i+1}/{len(chunks)} ({len(chunk)} chars)")
            audio = _synthesize_chunk(client, chunk, voice_id, output_format)
            if audio:
                audio_parts.append(audio)
            else:
                logger.warning(f"Failed to synthesize chunk {i+1}")

        if not audio_parts:
            return None

        # Concatenate all audio parts
        # For MP3, we can simply concatenate the bytes
        return b''.join(audio_parts)

    except NoCredentialsError:
        logger.error("Polly Error: No AWS credentials found.")
        return None

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        logger.error(f"Polly ClientError ({error_code}): {e}")
        return None

    except Exception as e:
        logger.error(f"Polly Error: {e}", exc_info=True)
        return None


async def synthesize_speech(
    text: str,
    voice_id: str = "Matthew",
    output_format: str = "mp3"
) -> Optional[bytes]:
    """
    Synthesize speech from text using Amazon Polly.

    Args:
        text: Text to convert to speech
        voice_id: Polly voice ID (e.g., "Matthew", "Joanna", "Amy", "Brian")
        output_format: Audio format ("mp3", "ogg_vorbis", "pcm")

    Returns:
        Audio bytes in the specified format, or None if failed
    """
    client = _get_polly_client()

    # Run synchronous boto3 call in thread pool
    result = await asyncio.to_thread(
        _sync_synthesize_speech, client, text, voice_id, output_format
    )

    return result


def get_available_voices() -> list:
    """
    Get list of available Polly voices.

    Returns:
        List of voice info dicts
    """
    try:
        client = _get_polly_client()
        response = client.describe_voices(LanguageCode='en-US')
        return response.get('Voices', [])
    except Exception as e:
        logger.error(f"Error getting Polly voices: {e}")
        return []
