"""FastAPI backend for LLM Council."""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
import json
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

from . import storage
from .council import run_full_council, generate_conversation_title, stage1_collect_responses, stage2_collect_rankings, stage3_synthesize_final, calculate_aggregate_rankings, perform_web_search
from .polly import synthesize_speech

app = FastAPI(title="LLM Council API")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateConversationRequest(BaseModel):
    """Request to create a new conversation."""
    pass


class SendMessageRequest(BaseModel):
    """Request to send a message in a conversation."""
    content: str


class ConversationMetadata(BaseModel):
    """Conversation metadata for list view."""
    id: str
    created_at: str
    title: str
    message_count: int


def build_conversation_context(conversation: dict, max_turns: int = 3) -> List[Dict[str, str]]:
    """
    Build message history from previous turns for multi-turn context.

    Args:
        conversation: The conversation dict with messages
        max_turns: Maximum number of previous turns to include

    Returns:
        List of message dicts with role and content
    """
    context = []
    messages = conversation.get("messages", [])

    # Get last N turns (user + assistant pairs)
    # Each turn = 2 messages, so get last max_turns * 2 messages
    recent_messages = messages[-(max_turns * 2):]

    for msg in recent_messages:
        if msg["role"] == "user":
            context.append({"role": "user", "content": msg["content"]})
        elif msg["role"] == "assistant" and msg.get("stage3"):
            # Include the final council response as assistant context
            stage3_response = msg["stage3"].get("response", "")
            if stage3_response:
                context.append({
                    "role": "assistant",
                    "content": stage3_response
                })

    return context


class Conversation(BaseModel):
    """Full conversation with all messages."""
    id: str
    created_at: str
    title: str
    messages: List[Dict[str, Any]]


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "LLM Council API"}


@app.get("/api/conversations", response_model=List[ConversationMetadata])
async def list_conversations():
    """List all conversations (metadata only)."""
    return storage.list_conversations()


@app.post("/api/conversations", response_model=Conversation)
async def create_conversation(request: CreateConversationRequest):
    """Create a new conversation."""
    conversation_id = str(uuid.uuid4())
    conversation = storage.create_conversation(conversation_id)
    return conversation


@app.get("/api/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    """Get a specific conversation with all its messages."""
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@app.post("/api/conversations/{conversation_id}/message")
async def send_message(conversation_id: str, request: SendMessageRequest):
    """
    Send a message and run the 3-stage council process.
    Returns the complete response with all stages.
    """
    # Check if conversation exists
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Check if this is the first message
    is_first_message = len(conversation["messages"]) == 0

    # Build conversation context from previous turns (before adding new message)
    conversation_history = build_conversation_context(conversation, max_turns=3)

    # Add user message
    storage.add_user_message(conversation_id, request.content)

    # If this is the first message, generate a title
    if is_first_message:
        title = await generate_conversation_title(request.content)
        storage.update_conversation_title(conversation_id, title)

    # Run the 3-stage council process with conversation history
    stage1_results, stage2_results, stage3_result, metadata = await run_full_council(
        request.content,
        conversation_history=conversation_history if conversation_history else None
    )

    # Add assistant message with all stages
    storage.add_assistant_message(
        conversation_id,
        stage1_results,
        stage2_results,
        stage3_result
    )

    # Return the complete response with metadata
    return {
        "stage1": stage1_results,
        "stage2": stage2_results,
        "stage3": stage3_result,
        "metadata": metadata
    }


@app.post("/api/conversations/{conversation_id}/message/stream")
async def send_message_stream(conversation_id: str, request: SendMessageRequest):
    """
    Send a message and stream the 3-stage council process.
    Returns Server-Sent Events as each stage completes.
    """
    # Check if conversation exists
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Check if this is the first message
    is_first_message = len(conversation["messages"]) == 0

    # Build conversation context from previous turns (before adding new message)
    conversation_history = build_conversation_context(conversation, max_turns=3)

    async def event_generator():
        try:
            logger.info(f"Stream: Starting council for query: {request.content[:100]}")

            # Add user message
            storage.add_user_message(conversation_id, request.content)

            # Start title generation in parallel (don't await yet)
            title_task = None
            if is_first_message:
                title_task = asyncio.create_task(generate_conversation_title(request.content))

            # Perform web search for real-time information
            logger.info("Stream: Performing web search...")
            web_context = await perform_web_search(request.content)
            if web_context:
                logger.info(f"Stream: Web search returned {len(web_context)} chars")
            else:
                logger.info("Stream: Web search returned None")

            # Stage 1: Collect responses (with conversation history and web context)
            logger.info("Stream: Starting Stage 1...")
            yield f"data: {json.dumps({'type': 'stage1_start'})}\n\n"
            stage1_results = await stage1_collect_responses(
                request.content,
                conversation_history if conversation_history else None,
                web_context
            )
            logger.info(f"Stream: Stage 1 complete - {len(stage1_results)} models responded")
            yield f"data: {json.dumps({'type': 'stage1_complete', 'data': stage1_results})}\n\n"

            # Stage 2: Collect rankings
            logger.info("Stream: Starting Stage 2...")
            yield f"data: {json.dumps({'type': 'stage2_start'})}\n\n"
            stage2_results, label_to_model = await stage2_collect_rankings(request.content, stage1_results)
            aggregate_rankings = calculate_aggregate_rankings(stage2_results, label_to_model)
            logger.info(f"Stream: Stage 2 complete - {len(stage2_results)} rankings collected")
            yield f"data: {json.dumps({'type': 'stage2_complete', 'data': stage2_results, 'metadata': {'label_to_model': label_to_model, 'aggregate_rankings': aggregate_rankings}})}\n\n"

            # Stage 3: Synthesize final answer
            logger.info("Stream: Starting Stage 3...")
            yield f"data: {json.dumps({'type': 'stage3_start'})}\n\n"
            stage3_result = await stage3_synthesize_final(request.content, stage1_results, stage2_results)
            logger.info(f"Stream: Stage 3 complete - Chairman: {stage3_result.get('model', 'unknown')}")
            yield f"data: {json.dumps({'type': 'stage3_complete', 'data': stage3_result})}\n\n"

            # Wait for title generation if it was started
            if title_task:
                title = await title_task
                storage.update_conversation_title(conversation_id, title)
                yield f"data: {json.dumps({'type': 'title_complete', 'data': {'title': title}})}\n\n"

            # Save complete assistant message
            storage.add_assistant_message(
                conversation_id,
                stage1_results,
                stage2_results,
                stage3_result
            )

            # Send completion event
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"

        except Exception as e:
            # Send error event
            logger.error(f"Stream: Exception occurred: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


class SpeakRequest(BaseModel):
    """Request to synthesize speech."""
    voice_id: str = "Matthew"
    message_index: int = -1  # -1 means latest


@app.post("/api/conversations/{conversation_id}/speak")
async def speak_response(conversation_id: str, request: SpeakRequest = None):
    """
    Synthesize speech for a Stage 3 response.
    Returns MP3 audio.
    """
    if request is None:
        request = SpeakRequest()

    # Get the conversation
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Find assistant messages
    assistant_messages = [
        msg for msg in conversation["messages"]
        if msg.get("role") == "assistant"
    ]

    if not assistant_messages:
        raise HTTPException(status_code=404, detail="No assistant response found")

    # Select message by index (-1 for latest)
    msg_index = request.message_index
    if msg_index < 0:
        msg_index = len(assistant_messages) + msg_index  # Convert negative to positive

    if msg_index < 0 or msg_index >= len(assistant_messages):
        raise HTTPException(status_code=404, detail="Message index out of range")

    selected_message = assistant_messages[msg_index]

    # Extract Stage 3 content
    stage3 = selected_message.get("stage3", {})
    text = stage3.get("response", "")

    if not text:
        raise HTTPException(status_code=400, detail="No Stage 3 response to synthesize")

    # Synthesize speech
    audio_bytes = await synthesize_speech(text, voice_id=request.voice_id)

    if audio_bytes is None:
        raise HTTPException(status_code=500, detail="Failed to synthesize speech")

    # Return audio as streaming response
    return StreamingResponse(
        iter([audio_bytes]),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline; filename=response.mp3"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
