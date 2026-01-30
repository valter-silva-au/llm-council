"""Deliberation archive system for LLM Council.

Saves council deliberations in a structured format for future reference.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

logger = logging.getLogger("llm_council.deliberations")

# Base directory for all deliberations
DELIBERATIONS_DIR = Path(__file__).parent.parent / "deliberations"


def create_slug(text: str, max_length: int = 50) -> str:
    """
    Create a URL-safe slug from text.

    Args:
        text: The text to slugify
        max_length: Maximum length of slug

    Returns:
        A URL-safe slug
    """
    # Convert to lowercase
    slug = text.lower()

    # Remove special characters, keep only alphanumeric and spaces
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)

    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)

    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)

    # Trim to max length
    slug = slug[:max_length].strip('-')

    return slug


def save_deliberation(
    question: str,
    stage1_results: List[Dict[str, Any]],
    stage2_results: List[Dict[str, Any]],
    stage3_result: Dict[str, Any],
    metadata: Dict[str, Any],
    web_context: Optional[str] = None
) -> str:
    """
    Save a complete council deliberation to structured storage.

    Args:
        question: The original user question
        stage1_results: Individual model responses
        stage2_results: Model rankings
        stage3_result: Chairman's final answer
        metadata: Additional metadata (label_to_model, aggregate_rankings)
        web_context: Optional web search context used

    Returns:
        Path to the deliberation directory
    """
    # Create timestamp and slug
    timestamp = datetime.now()
    date_str = timestamp.strftime("%Y-%m-%d")
    time_str = timestamp.strftime("%H-%M-%S")

    # Create slug from question (first 50 chars)
    question_slug = create_slug(question)

    # Create directory name: YYYY-MM-DD-HH-MM-SS-slug
    dir_name = f"{date_str}-{time_str}-{question_slug}"
    delib_dir = DELIBERATIONS_DIR / dir_name

    # Create directory structure
    delib_dir.mkdir(parents=True, exist_ok=True)
    (delib_dir / "stage1").mkdir(exist_ok=True)
    (delib_dir / "stage2").mkdir(exist_ok=True)
    (delib_dir / "stage3").mkdir(exist_ok=True)

    logger.info(f"Saving deliberation to: {delib_dir}")

    # Save metadata
    metadata_content = {
        "timestamp": timestamp.isoformat(),
        "date": date_str,
        "time": time_str,
        "question_preview": question[:200],
        "models_participated": len(stage1_results),
        "chairman": stage3_result.get("model", "unknown"),
        "web_search_enabled": web_context is not None,
        "label_to_model": metadata.get("label_to_model", {}),
        "aggregate_rankings": metadata.get("aggregate_rankings", [])
    }

    with open(delib_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata_content, f, indent=2, ensure_ascii=False)

    # Save question
    with open(delib_dir / "question.md", "w", encoding="utf-8") as f:
        f.write(f"# Council Deliberation\n\n")
        f.write(f"**Date:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Question:**\n\n{question}\n")

        if web_context:
            f.write(f"\n---\n\n**Web Search Context Provided:**\n\n```\n{web_context[:500]}...\n```\n")

    # Save Stage 1: Individual responses
    for i, resp in enumerate(stage1_results, 1):
        model_name = resp["model"]
        safe_name = create_slug(model_name) or f"model-{i}"

        with open(delib_dir / "stage1" / f"{safe_name}.md", "w", encoding="utf-8") as f:
            f.write(f"# {model_name}\n\n")
            f.write(f"**Stage 1 Response**\n\n")
            f.write(f"{resp['response']}\n")

    # Save Stage 2: Rankings
    rankings_data = []
    for ranking in stage2_results:
        rankings_data.append({
            "model": ranking["model"],
            "ranking": ranking.get("parsed_ranking", []),
            "full_evaluation": ranking["ranking"]
        })

    with open(delib_dir / "stage2" / "rankings.json", "w", encoding="utf-8") as f:
        json.dump(rankings_data, f, indent=2, ensure_ascii=False)

    # Save Stage 2: Human-readable rankings
    with open(delib_dir / "stage2" / "rankings.md", "w", encoding="utf-8") as f:
        f.write("# Stage 2: Peer Rankings\n\n")
        for i, ranking in enumerate(stage2_results, 1):
            f.write(f"## {ranking['model']}\n\n")
            f.write(f"{ranking['ranking']}\n\n")
            f.write("---\n\n")

    # Save Stage 3: Final answer
    with open(delib_dir / "stage3" / "final-answer.md", "w", encoding="utf-8") as f:
        f.write(f"# Final Council Answer\n\n")
        f.write(f"**Chairman:** {stage3_result.get('model', 'unknown')}\n\n")
        f.write("---\n\n")
        f.write(f"{stage3_result.get('response', 'No response')}\n")

    # Save complete deliberation in one file
    with open(delib_dir / "full-deliberation.md", "w", encoding="utf-8") as f:
        f.write("# Complete Council Deliberation\n\n")
        f.write(f"**Date:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        f.write("## Question\n\n")
        f.write(f"{question}\n\n")

        if web_context:
            f.write("### Web Search Context\n\n")
            f.write(f"```\n{web_context[:1000]}...\n```\n\n")

        f.write("---\n\n")
        f.write("## Stage 1: Individual Responses\n\n")
        for resp in stage1_results:
            f.write(f"### {resp['model']}\n\n")
            f.write(f"{resp['response']}\n\n")
            f.write("---\n\n")

        f.write("## Stage 2: Peer Rankings\n\n")
        for ranking in stage2_results:
            f.write(f"### {ranking['model']}\n\n")
            f.write(f"{ranking['ranking']}\n\n")
            f.write("---\n\n")

        f.write("## Stage 3: Final Answer\n\n")
        f.write(f"**Chairman:** {stage3_result.get('model', 'unknown')}\n\n")
        f.write(f"{stage3_result.get('response', 'No response')}\n\n")

    logger.info(f"✓ Deliberation saved successfully: {dir_name}")

    return str(delib_dir)


def list_deliberations(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    List all saved deliberations, sorted by date (newest first).

    Args:
        limit: Optional limit on number of results

    Returns:
        List of deliberation metadata dicts
    """
    if not DELIBERATIONS_DIR.exists():
        return []

    deliberations = []

    for delib_dir in sorted(DELIBERATIONS_DIR.iterdir(), reverse=True):
        if not delib_dir.is_dir():
            continue

        metadata_file = delib_dir / "metadata.json"
        if not metadata_file.exists():
            continue

        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
                metadata["path"] = str(delib_dir)
                metadata["name"] = delib_dir.name
                deliberations.append(metadata)
        except Exception as e:
            logger.error(f"Error reading metadata from {delib_dir}: {e}")

    if limit:
        deliberations = deliberations[:limit]

    return deliberations


def get_deliberation(name_or_path: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific deliberation by name or path.

    Args:
        name_or_path: Directory name or full path

    Returns:
        Dict with all deliberation data, or None if not found
    """
    # Try as direct path first
    delib_dir = Path(name_or_path)
    if not delib_dir.exists():
        # Try as name within deliberations directory
        delib_dir = DELIBERATIONS_DIR / name_or_path

    if not delib_dir.exists():
        logger.warning(f"Deliberation not found: {name_or_path}")
        return None

    try:
        # Load metadata
        with open(delib_dir / "metadata.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        # Load question
        with open(delib_dir / "question.md", "r", encoding="utf-8") as f:
            data["question"] = f.read()

        # Load Stage 1 responses
        data["stage1"] = []
        stage1_dir = delib_dir / "stage1"
        if stage1_dir.exists():
            for response_file in sorted(stage1_dir.glob("*.md")):
                with open(response_file, "r", encoding="utf-8") as f:
                    data["stage1"].append({
                        "file": response_file.name,
                        "content": f.read()
                    })

        # Load Stage 2 rankings
        rankings_file = delib_dir / "stage2" / "rankings.json"
        if rankings_file.exists():
            with open(rankings_file, "r", encoding="utf-8") as f:
                data["stage2"] = json.load(f)

        # Load Stage 3 final answer
        final_answer_file = delib_dir / "stage3" / "final-answer.md"
        if final_answer_file.exists():
            with open(final_answer_file, "r", encoding="utf-8") as f:
                data["stage3"] = f.read()

        data["path"] = str(delib_dir)
        data["name"] = delib_dir.name

        return data

    except Exception as e:
        logger.error(f"Error loading deliberation {name_or_path}: {e}")
        return None


def search_deliberations(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search deliberations by question content.

    Args:
        query: Search query
        limit: Maximum results to return

    Returns:
        List of matching deliberation metadata
    """
    query_lower = query.lower()
    results = []

    for delib in list_deliberations():
        question_preview = delib.get("question_preview", "").lower()
        if query_lower in question_preview:
            results.append(delib)
            if len(results) >= limit:
                break

    return results
