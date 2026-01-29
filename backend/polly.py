"""Amazon Polly TTS client for voice synthesis.

NOTE: Polly requires standard AWS credentials (access key + secret key).
The Bedrock-specific bearer token does not work with Polly.
Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables,
or configure credentials via ~/.aws/credentials.
"""

import asyncio
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from typing import Optional
from .config import AWS_REGION


def _get_polly_client():
    """Create a Polly client."""
    return boto3.client(
        'polly',
        region_name=AWS_REGION
    )


def _sync_synthesize_speech(
    client,
    text: str,
    voice_id: str = "Matthew",
    output_format: str = "mp3"
) -> Optional[bytes]:
    """
    Synchronous speech synthesis (runs in thread pool).

    Args:
        client: Boto3 Polly client
        text: Text to synthesize
        voice_id: Polly voice ID (e.g., "Matthew", "Joanna", "Amy")
        output_format: Audio format ("mp3", "ogg_vorbis", "pcm")

    Returns:
        Audio bytes or None if failed
    """
    try:
        # Use neural engine for better quality
        response = client.synthesize_speech(
            Text=text,
            OutputFormat=output_format,
            VoiceId=voice_id,
            Engine='neural'
        )

        # Read the audio stream
        audio_stream = response.get('AudioStream')
        if audio_stream:
            return audio_stream.read()

        return None

    except NoCredentialsError:
        print("Polly Error: No AWS credentials found.")
        print("  Polly requires standard AWS credentials (access key + secret key).")
        print("  The Bedrock bearer token does not work with Polly.")
        print("  Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
        return None

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code == 'InvalidParameterValue':
            # Fallback to standard engine if neural not available for this voice
            try:
                response = client.synthesize_speech(
                    Text=text,
                    OutputFormat=output_format,
                    VoiceId=voice_id,
                    Engine='standard'
                )
                audio_stream = response.get('AudioStream')
                if audio_stream:
                    return audio_stream.read()
            except Exception as e2:
                print(f"Polly Error (standard engine): {e2}")
        else:
            print(f"Polly Error: {e}")
        return None

    except Exception as e:
        print(f"Polly Error: {e}")
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
        print(f"Error getting Polly voices: {e}")
        return []
