#!/usr/bin/env python3
"""Test script to diagnose Stage 3 Chairman synthesis issues."""

import asyncio
import sys
import logging
from backend.config import CHAIRMAN_MODEL, API_PROVIDER

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Enable detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


async def test_stage3_realistic():
    """Test Chairman with realistic Stage 3 context size."""
    print("🔍 Testing Stage 3 Chairman Synthesis")
    print("=" * 60)
    print(f"API Provider: {API_PROVIDER}")
    print(f"Chairman Model: {CHAIRMAN_MODEL}")
    print("=" * 60)

    # Import the appropriate query function
    if API_PROVIDER == "bedrock":
        from backend.bedrock import query_model
    else:
        from backend.openrouter import query_model

    # Simulate realistic Stage 3 prompt with multiple model responses
    stage1_responses = """
Model: us.anthropic.claude-opus-4-5-20251101-v1:0
Response: The latest AI developments include significant advances in multimodal models, improved reasoning capabilities, and enhanced safety measures. Notable releases include GPT-5.1, Gemini 3.0, and Claude Sonnet 4.5. These models demonstrate better performance on complex reasoning tasks and show improved ability to follow instructions while maintaining safety guardrails.

Model: us.deepseek.r1-v1:0
Response: Recent AI progress focuses on several key areas: (1) Chain-of-thought reasoning improvements, (2) Mixture-of-experts architectures for efficient scaling, (3) Constitutional AI for better alignment, (4) Reduced hallucination rates through retrieval augmentation, and (5) Enhanced few-shot learning capabilities. Benchmarks show 15-20% improvements across standard evaluations.

Model: mistral.mistral-large-2407-v1:0
Response: 2026's AI landscape is characterized by rapid iteration and democratization. Open-source models now rival proprietary ones in many tasks. Key trends include edge AI deployment, domain-specific fine-tuning becoming mainstream, and increased focus on energy efficiency. Regulatory frameworks like the EU AI Act are shaping development priorities.

Model: us.amazon.nova-premier-v1:0
Response: The AI field is experiencing convergence across vision, language, and reasoning. Practical applications in healthcare, education, and scientific research are expanding. Notable improvements in code generation, mathematical reasoning, and multilingual capabilities. Industry focus has shifted toward reliability, reproducibility, and real-world deployment challenges.
"""

    stage2_rankings = """
Model: us.anthropic.claude-opus-4-5-20251101-v1:0
Ranking: Response A provides comprehensive coverage of recent model releases and capabilities. Response B offers detailed technical insights but could be more accessible. Response C excels at contextualizing trends within regulatory and market forces. Response D balances breadth and practical applications effectively.
FINAL RANKING:
1. Response D
2. Response A
3. Response C
4. Response B

Model: us.deepseek.r1-v1:0
Ranking: Evaluating technical depth and accuracy: Response B demonstrates strong technical grounding with specific architectural details. Response A is well-rounded but somewhat surface-level. Response C provides valuable industry context. Response D effectively bridges technical and practical perspectives.
FINAL RANKING:
1. Response B
2. Response D
3. Response A
4. Response C

Model: mistral.mistral-large-2407-v1:0
Ranking: Assessing comprehensiveness and relevance: Response C offers crucial context about the broader AI ecosystem including regulatory and market dynamics. Response D provides balanced coverage. Response A covers recent releases well. Response B is technically sound but narrow in scope.
FINAL RANKING:
1. Response C
2. Response D
3. Response A
4. Response B

Model: us.amazon.nova-premier-v1:0
Ranking: Considering practical value and clarity: Response D excels at connecting developments to real-world applications. Response A provides clear overview of recent releases. Response C adds important industry perspective. Response B is technically detailed but less accessible.
FINAL RANKING:
1. Response D
2. Response A
3. Response C
4. Response B
"""

    chairman_prompt = f"""You are the Chairman of an LLM Council. Multiple AI models have provided responses to a user's question, and then ranked each other's responses.

Original Question: What are the latest AI developments?

STAGE 1 - Individual Responses:
{stage1_responses}

STAGE 2 - Peer Rankings:
{stage2_rankings}

Your task as Chairman is to synthesize all of this information into a single, comprehensive, accurate answer to the user's original question. Consider:
- The individual responses and their insights
- The peer rankings and what they reveal about response quality
- Any patterns of agreement or disagreement

Provide a clear, well-reasoned final answer that represents the council's collective wisdom:"""

    messages = [{"role": "user", "content": chairman_prompt}]

    prompt_length = len(chairman_prompt)
    estimated_tokens = prompt_length // 4

    print(f"\n📊 Prompt Statistics:")
    print(f"  Length: {prompt_length:,} characters")
    print(f"  Estimated: ~{estimated_tokens:,} tokens")
    print(f"  Timeout: 180 seconds")
    print("-" * 60)

    print("\n📤 Sending Stage 3 prompt to Chairman...")

    try:
        response = await query_model(CHAIRMAN_MODEL, messages, timeout=180.0)

        if response is None:
            print("\n❌ FAILED! Chairman returned None")
            print("\nPossible causes:")
            print("  1. Timeout (180 seconds exceeded)")
            print("  2. Model throttling/quota limits")
            print("  3. Context window exceeded (unlikely with Nova Premier)")
            print("  4. Temporary service issue")
            print("\nCheck the detailed logs above for the specific error.")
            return False
        else:
            content = response.get('content', '')
            print(f"\n✅ SUCCESS! Chairman synthesized response")
            print(f"Response length: {len(content)} characters")
            print("-" * 60)
            print("Synthesis preview:")
            print(content[:800])
            if len(content) > 800:
                print("...")
            return True

    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main entry point."""
    try:
        success = await test_stage3_realistic()
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
